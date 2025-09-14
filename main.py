from __future__ import annotations

import os
import socket
from datetime import datetime

from typing import Dict, List
from uuid import UUID

from fastapi import FastAPI, HTTPException
from fastapi import Query, Path
from typing import Optional

from models.person import PersonCreate, PersonRead, PersonUpdate
from models.address import AddressCreate, AddressRead, AddressUpdate
from models.health import Health
from models.classroom import ClassroomCreate, ClassroomRead, ClassroomUpdate
from models.desk import DeskCreate, DeskRead, DeskUpdate

port = int(os.environ.get("FASTAPIPORT", 8000))

# -----------------------------------------------------------------------------
# Fake in-memory "databases"
# -----------------------------------------------------------------------------
# persons: Dict[UUID, PersonRead] = {}
# addresses: Dict[UUID, AddressRead] = {}

# app = FastAPI(
#     title="Person/Address API",
#     description="Demo FastAPI app using Pydantic v2 models for Person and Address",
#     version="0.1.0",
# )

classrooms: Dict[UUID, ClassroomRead] = {}
desks: Dict[UUID, DeskRead] = {}

app = FastAPI(
    title="Classroom/Desk API",
    description="Demo FastAPI app using Pydantic v2 models for Classroom and Desk",
    version="0.1.0",
)

# -----------------------------------------------------------------------------
# Desk endpoints
# -----------------------------------------------------------------------------

def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
    return Health(
        status=200,
        status_message="OK",
        timestamp=datetime.utcnow().isoformat() + "Z",
        ip_address=socket.gethostbyname(socket.gethostname()),
        echo=echo,
        path_echo=path_echo
    )

@app.get("/health", response_model=Health)
def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
    # Works because path_echo is optional in the model
    return make_health(echo=echo, path_echo=None)

@app.get("/health/{path_echo}", response_model=Health)
def get_health_with_path(
    path_echo: str = Path(..., description="Required echo in the URL path"),
    echo: str | None = Query(None, description="Optional echo string"),
):
    return make_health(echo=echo, path_echo=path_echo)

@app.post("/desks", response_model=DeskRead, status_code=201)
def create_desk(desk: DeskCreate):
    if desk.id in desks:
        raise HTTPException(status_code=400, detail="Desk with this ID already exists")
    desks[desk.id] = DeskRead(**desk.model_dump())
    return desks[desk.id]

@app.get("/desks", response_model=List[DeskRead])
def list_desks(
    label: Optional[str] = Query(None, description="Filter by label"),
    hand_config: Optional[str] = Query(None, description="Filter by left/right desk configuration"),
):
    results = list(desks.values())

    if label is not None:
        results = [a for a in results if a.label == label]
    if hand_config is not None:
        results = [a for a in results if a.hand_config == hand_config]

    return results

@app.get("/desks/{desk_id}", response_model=DeskRead)
def get_desk(desk_id: UUID):
    if desk_id not in desks:
        raise HTTPException(status_code=404, detail="Desk not found")
    return desks[desk_id]

@app.patch("/desks/{desk_id}", response_model=DeskRead)
def update_desk(desk_id: UUID, update: DeskUpdate):
    if desk_id not in desks:
        raise HTTPException(status_code=404, detail="Desk not found")
    stored = desks[desk_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    desks[desk_id] = DeskRead(**stored)
    return desks[desk_id]

@app.put("/desks/{desk_id}", response_model=DeskRead)
def replace_desk(desk_id: UUID, desk: DeskCreate):
    """
    Fully replace a desk resource or create a new one if it doesn't exist.
    Note that changes to the ID will be ignored.
    """
    if desk_id not in desks:
        new_desk_data = desk.model_dump()
        new_desk_data["id"] = desk_id
        return create_desk(DeskCreate(**new_desk_data))
    stored = desks[desk_id]
    new_data = desk.model_dump()
    new_desk = DeskRead(
        id=desk_id,
        label=new_data["label"],
        hand_config=new_data["hand_config"],
        created_at=stored.created_at,
        updated_at=datetime.utcnow(),
    )
    desks[desk_id] = new_desk
    return new_desk

@app.delete("/desks/{desk_id}")
def delete_desk(desk_id: UUID):
    if desk_id not in desks:
        raise HTTPException(status_code=404, detail="Desk not found")
    del desks[desk_id]
    return {"confirmation": "Desk deleted successfully"}

# -----------------------------------------------------------------------------
# Classroom endpoints
# -----------------------------------------------------------------------------
@app.post("/classrooms", response_model=ClassroomRead, status_code=201)
def create_classroom(classroom: ClassroomCreate):
    # Each classroom gets its own UUID; stored as ClassroomRead
    classroom_read = ClassroomRead(**classroom.model_dump())
    classrooms[classroom_read.id] = classroom_read
    return classroom_read

@app.get("/classrooms", response_model=List[ClassroomRead])
def list_classrooms(
    room_no: Optional[str] = Query(None, description="Filter by room number"),
    building: Optional[str] = Query(None, description="Filter by building"),
    university: Optional[str] = Query(None, description="Filter by university name"),
    label: Optional[str] = Query(None, description="Filter by label of at least one desk"),
    hand_config: Optional[str] = Query(None, description="Filter by left/right desk configuration of at least one desk"),
):
    results = list(desks.values())

    if room_no is not None:
        results = [p for p in results if p.room_no == room_no]
    if building is not None:
        results = [p for p in results if p.building == building]
    if university is not None:
        results = [p for p in results if p.university == university]

    # nested desk filtering
    if label is not None:
        results = [p for p in results if any(desk.label == label for desk in p.desks)]
    if hand_config is not None:
        results = [p for p in results if any(desk.hand_config == hand_config for desk in p.desks)]

    return results

@app.get("/classrooms/{classroom_id}", response_model=ClassroomRead)
def get_classrooom(classroom_id: UUID):
    if classroom_id not in classrooms:
        raise HTTPException(status_code=404, detail="Classroom not found")
    return classrooms[classroom_id]

@app.patch("/classrooms/{classroom_id}", response_model=ClassroomRead)
def update_classroom(classroom_id: UUID, update: ClassroomUpdate):
    if classroom_id not in classrooms:
        raise HTTPException(status_code=404, detail="Classroom not found")
    stored = classrooms[classroom_id].model_dump()
    stored.update(update.model_dump(exclude_unset=True))
    classrooms[classroom_id] = ClassroomRead(**stored)
    return classrooms[classroom_id]

@app.put("/classrooms/{classroom_id}", response_model=ClassroomRead)
def replace_classroom(classroom_id: UUID, classroom: ClassroomCreate):
    """
    Fully replace a classroom resource or create a new one if it doesn't exist.
    Note that changes to the ID will be ignored.
    """
    if classroom_id not in classrooms:
        new_classroom_data = classroom.model_dump()
        new_classroom_data["id"] = classroom_id
        return create_desk(DeskCreate(**new_classroom_data))
    stored = classrooms[classroom_id]
    new_data = classroom.model_dump()
    new_classroom = ClassroomRead(
        id=classroom_id,
        room_no=new_data["room_no"],
        building=new_data["building"],
        university=new_data["university"],
        desks=new_data["desks"],
        created_at=stored.created_at,
        updated_at=datetime.utcnow(),
    )
    classrooms[classroom_id] = new_classroom
    return new_classroom

@app.delete("/classrooms/{classroom_id}")
def delete_classroom(classroom_id: UUID):
    if classroom_id not in classrooms:
        raise HTTPException(status_code=404, detail="Classroom not found")
    del classrooms[classroom_id]
    return {"confirmation": "Classroom deleted successfully"}

# # -----------------------------------------------------------------------------
# # Address endpoints
# # -----------------------------------------------------------------------------

# def make_health(echo: Optional[str], path_echo: Optional[str]=None) -> Health:
#     return Health(
#         status=200,
#         status_message="OK",
#         timestamp=datetime.utcnow().isoformat() + "Z",
#         ip_address=socket.gethostbyname(socket.gethostname()),
#         echo=echo,
#         path_echo=path_echo
#     )

# @app.get("/health", response_model=Health)
# def get_health_no_path(echo: str | None = Query(None, description="Optional echo string")):
#     # Works because path_echo is optional in the model
#     return make_health(echo=echo, path_echo=None)

# @app.get("/health/{path_echo}", response_model=Health)
# def get_health_with_path(
#     path_echo: str = Path(..., description="Required echo in the URL path"),
#     echo: str | None = Query(None, description="Optional echo string"),
# ):
#     return make_health(echo=echo, path_echo=path_echo)

# @app.post("/addresses", response_model=AddressRead, status_code=201)
# def create_address(address: AddressCreate):
#     if address.id in addresses:
#         raise HTTPException(status_code=400, detail="Address with this ID already exists")
#     addresses[address.id] = AddressRead(**address.model_dump())
#     return addresses[address.id]

# @app.get("/addresses", response_model=List[AddressRead])
# def list_addresses(
#     street: Optional[str] = Query(None, description="Filter by street"),
#     city: Optional[str] = Query(None, description="Filter by city"),
#     state: Optional[str] = Query(None, description="Filter by state/region"),
#     postal_code: Optional[str] = Query(None, description="Filter by postal code"),
#     country: Optional[str] = Query(None, description="Filter by country"),
# ):
#     results = list(addresses.values())

#     if street is not None:
#         results = [a for a in results if a.street == street]
#     if city is not None:
#         results = [a for a in results if a.city == city]
#     if state is not None:
#         results = [a for a in results if a.state == state]
#     if postal_code is not None:
#         results = [a for a in results if a.postal_code == postal_code]
#     if country is not None:
#         results = [a for a in results if a.country == country]

#     return results

# @app.get("/addresses/{address_id}", response_model=AddressRead)
# def get_address(address_id: UUID):
#     if address_id not in addresses:
#         raise HTTPException(status_code=404, detail="Address not found")
#     return addresses[address_id]

# @app.patch("/addresses/{address_id}", response_model=AddressRead)
# def update_address(address_id: UUID, update: AddressUpdate):
#     if address_id not in addresses:
#         raise HTTPException(status_code=404, detail="Address not found")
#     stored = addresses[address_id].model_dump()
#     stored.update(update.model_dump(exclude_unset=True))
#     addresses[address_id] = AddressRead(**stored)
#     return addresses[address_id]

# # -----------------------------------------------------------------------------
# # Person endpoints
# # -----------------------------------------------------------------------------
# @app.post("/persons", response_model=PersonRead, status_code=201)
# def create_person(person: PersonCreate):
#     # Each person gets its own UUID; stored as PersonRead
#     person_read = PersonRead(**person.model_dump())
#     persons[person_read.id] = person_read
#     return person_read

# @app.get("/persons", response_model=List[PersonRead])
# def list_persons(
#     uni: Optional[str] = Query(None, description="Filter by Columbia UNI"),
#     first_name: Optional[str] = Query(None, description="Filter by first name"),
#     last_name: Optional[str] = Query(None, description="Filter by last name"),
#     email: Optional[str] = Query(None, description="Filter by email"),
#     phone: Optional[str] = Query(None, description="Filter by phone number"),
#     birth_date: Optional[str] = Query(None, description="Filter by date of birth (YYYY-MM-DD)"),
#     city: Optional[str] = Query(None, description="Filter by city of at least one address"),
#     country: Optional[str] = Query(None, description="Filter by country of at least one address"),
# ):
#     results = list(persons.values())

#     if uni is not None:
#         results = [p for p in results if p.uni == uni]
#     if first_name is not None:
#         results = [p for p in results if p.first_name == first_name]
#     if last_name is not None:
#         results = [p for p in results if p.last_name == last_name]
#     if email is not None:
#         results = [p for p in results if p.email == email]
#     if phone is not None:
#         results = [p for p in results if p.phone == phone]
#     if birth_date is not None:
#         results = [p for p in results if str(p.birth_date) == birth_date]

#     # nested address filtering
#     if city is not None:
#         results = [p for p in results if any(addr.city == city for addr in p.addresses)]
#     if country is not None:
#         results = [p for p in results if any(addr.country == country for addr in p.addresses)]

#     return results

# @app.get("/persons/{person_id}", response_model=PersonRead)
# def get_person(person_id: UUID):
#     if person_id not in persons:
#         raise HTTPException(status_code=404, detail="Person not found")
#     return persons[person_id]

# @app.patch("/persons/{person_id}", response_model=PersonRead)
# def update_person(person_id: UUID, update: PersonUpdate):
#     if person_id not in persons:
#         raise HTTPException(status_code=404, detail="Person not found")
#     stored = persons[person_id].model_dump()
#     stored.update(update.model_dump(exclude_unset=True))
#     persons[person_id] = PersonRead(**stored)
#     return persons[person_id]

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------
# @app.get("/")
# def root():
#     return {"message": "Welcome to the Person/Address API. See /docs for OpenAPI UI."}

@app.get("/")
def root():
    return {"message": "Welcome to the Classroom/Desk API. See /docs for OpenAPI UI."}

# -----------------------------------------------------------------------------
# Entrypoint for `python main.py`
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
