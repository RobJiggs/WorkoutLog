import enum
import calendar

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Enum as SQLEnum, Nullable
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase, relationship,declarative_base

from pydantic import BaseModel
from typing import Optional,List

from datetime import date as dt_date

class Worktype(enum.Enum):
    Weights="Weights"
    Basketball="Basketball"
    GymCardio="GymCardio"


app = FastAPI(title="Workouts")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="Templates")

engine=create_engine("sqlite:///workouts.db",connect_args={"check_same_thread":False})
SessionLocal=sessionmaker(bind=engine,autoflush=False,autocommit=False)
Base = declarative_base()

class Worksession(Base):
    __tablename__ = "worksession"

    id = Column(Integer,primary_key=True)
    date=Column(Date)
    work=Column(SQLEnum(Worktype))

    workouts= relationship("Workout",back_populates="worksession", cascade="all, delete-orphan")

class Workout(Base):
    __tablename__ = "workout"

    id = Column(Integer,primary_key=True)
    name=Column(String)
    desc=Column(String)

    worksession_id=Column(Integer,ForeignKey("worksession.id"),nullable=False)
    worksession=relationship("Worksession",back_populates="workouts")


Base.metadata.create_all(engine)

class CreateSession(BaseModel):
    date:dt_date
    work:Worktype


class CreateWork(BaseModel):
    desc:str
    name:str
    session_id:int
class SessionResponse(BaseModel):
    date:dt_date
    work:Worktype

    class config:
        from_attribute = True

class WorkResponse(BaseModel):
    desc:str
    name:str
    class config:
        from_attribute=True

class SessionUpdate(BaseModel):
    date: Optional[dt_date]=None
    work: Optional[Worktype]=None

class WorkUpdate(BaseModel):
    desc:Optional[str]=None
    name:Optional[str]=None


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

get_db()
@app.get("/all", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):

    worksessions=db.query(Worksession).order_by(Worksession.date.asc()).all()

    return templates.TemplateResponse(
    "home.html",
    {"request": request, "sessions":worksessions},
)

@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    begin_month=dt_date.today().replace(day=1)
    last_day=calendar.monthrange(begin_month.year, begin_month.month)[1]

    end_month=dt_date.today().replace(day=last_day)
    year=str(dt_date.today().year)[2:4]
    month_name=calendar.month_name[end_month.month]
    worksessions=db.query(Worksession).filter(Worksession.date.between(begin_month,end_month)).order_by(Worksession.date.asc()).all()

    return templates.TemplateResponse(
    "monthly.html",
    {"request": request, "sessions":worksessions,"month":month_name,"year":year},
)




@app.get("/worksessions")
def get_worksessions(db:Session=Depends(get_db)):
    allsessions=db.query(Worksession).all()
    return allsessions


@app.get("/workout/{workout_id}")
def get_workout(workout_id:int,db:Session=Depends(get_db)):
    workout=db.query(Workout).filter(Workout.id==workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.get("/workouts/{worksession_id}")
def get_workouts(worksession_id:int,db:Session=Depends(get_db)):
    worksession=db.query(Workout).filter(Workout.worksession_id == worksession_id).all()
    if not worksession:
        raise HTTPException(status_code=404, detail="Work session not found")
    return worksession


@app.post("/workouts",response_model=WorkResponse)
def create_workout(creatework:CreateWork,db:Session=Depends(get_db)):
    sesh=db.query(Worksession).filter(Worksession.id==creatework.session_id).first()
    if not sesh:
        raise HTTPException(status_code=404, detail="Work session not found")
    print(creatework.name)
    newwork=Workout(name=creatework.name, desc=creatework.desc, worksession_id=sesh.id)
    db.add(newwork)
    db.commit()
    db.refresh(newwork)

    return newwork


@app.post("/worksession",response_model=SessionResponse)
def create_worksession(createSession:CreateSession,db:Session=Depends(get_db)):
    newsession=Worksession(**createSession.dict())
    db.add(newsession)
    db.commit()
    db.refresh(newsession)
    return newsession

@app.patch("/worksession/{worksession_id}",response_model=SessionResponse)
def updatesession(worksession_id:int,sesh:SessionUpdate,db:Session=Depends(get_db)):
    dbsesh=db.query(Worksession).filter(Worksession.id==worksession_id).first()
    if not dbsesh:
        raise HTTPException(status_code=404, detail="Work session not found")
    updates=sesh.dict(exclude_unset=True)

    for attr, value in updates.items():
        setattr(dbsesh, attr, value)
    db.commit()
    db.refresh(dbsesh)
    return dbsesh

@app.patch("/workout/{workout_id}")
def updatework(workout_id:int,work:WorkUpdate,db:Session=Depends(get_db)):
    dbwork=db.query(Workout).filter(Workout.id==workout_id).first()
    if not dbwork:
        raise HTTPException(status_code=404, detail="Workout not found")
    updates=work.dict(exclude_unset=True)


    if "desc" in updates:
        dbwork.desc=updates["desc"]
        print(updates["desc"])
    if "name" in updates:
        dbwork.name=updates["name"]
        print(updates["name"])

    db.commit()
    db.refresh(dbwork)
    return dbwork

@app.delete("/workout/{workout_id}")
def deletework(workout_id:int,db:Session=Depends(get_db)):
    dbwork=db.query(Workout).filter(Workout.id==workout_id).first()
    if not dbwork:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(dbwork)
    db.commit()
    return {"message": f"Workout deleted"}


@app.delete("/worksession/{worksession_id}")
def deletesesh(worksession_id:int,db:Session=Depends(get_db)):
    dbsesh=db.query(Worksession).filter(Worksession.id==worksession_id).first()
    if not dbsesh:
        raise HTTPException(status_code=404, detail="Work session not found")
    db.delete(dbsesh)
    db.commit()
    return {"message": f"Work session deleted"}


@app.get("/session/cardio", response_class=HTMLResponse)
def cardio(request: Request, db: Session = Depends(get_db)):

    worksessions=db.query(Worksession).filter(Worksession.work == "GymCardio" ).all()




    return templates.TemplateResponse(
    "cardio.html",
    {"request": request, "sessions":worksessions},
)


@app.get("/session/weights", response_class=HTMLResponse)
def weights(request: Request, db: Session = Depends(get_db)):

    worksessions=db.query(Worksession).filter(Worksession.work == "Weights" ).all()

    return templates.TemplateResponse(
    "weights.html",
    {"request": request, "sessions":worksessions},
)


@app.get("/session/basketball", response_class=HTMLResponse)
def basketball(request: Request, db: Session = Depends(get_db)):

    worksessions=db.query(Worksession).filter(Worksession.work == "Basketball" ).all()

    return templates.TemplateResponse(
    "basketball.html",
    {"request": request, "sessions":worksessions},
)

@app.get("/session/best")
def best_count(request: Request, db: Session = Depends(get_db)):
    month_dict={}
    for i in range(1, 13):

        this_year = dt_date.today().year
        begin_month=dt_date.today().replace(month=i,day=1)
        last_day = calendar.monthrange(this_year, begin_month.month)[1]

        end_month = begin_month.replace(day=last_day)
        year = str(dt_date.today().year)[2:4]
        month_name = calendar.month_name[end_month.month]
        worksessions = db.query(Worksession).filter(Worksession.date.between(begin_month, end_month)).order_by(Worksession.date.asc()).all()
        count=0
        m_list = []

        if len(worksessions)>0:
            for worksession in worksessions:
                count+=db.query(Workout).filter(Workout.worksession_id==worksession.id).count()
                workouts=db.query(Workout).filter(Workout.worksession_id==worksession.id).all()


                for workout in workouts:
                    m_list.append(workout)
            m_list.append(count)
            m_list.reverse()
            month_dict[month_name + " '" + year] = m_list


        else:
            m_list.append(count)
            month_dict[month_name + " '" + year] = m_list



    return templates.TemplateResponse(
            "best.html",
            {"request": request, "sessions": worksessions,"month_dict":month_dict},
        )


