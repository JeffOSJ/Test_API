# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colab.
Original file is located at
    https://colab.research.google.com/drive/1PhwP1kdSJlVpEUcEqr95zUTjDJva0TnJ
"""

!pip install fastapi uvicorn nest-asyncio pyngrok sqlalchemy


from pyngrok import ngrok
import nest_asyncio
import uvicorn
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
engine = create_engine("sqlite:///dmcard.db", connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Cartao(Base):
    __tablename__ = "cartoes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    cpf = Column(String, unique=True, index=True)
    renda = Column(Float)
    score = Column(Integer)
    aprovado = Column(Boolean)
    limite = Column(Float)
    data = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)


class Solicitacao(BaseModel):
    nome: str
    cpf: str
    renda: float

@app.get("/cartoes")
def listar_cartoes():
    db = SessionLocal()
    return db.query(Cartao).order_by(Cartao.data).all()

@app.post("/cartoes")
def solicitar_cartao(dados: Solicitacao):
    db = SessionLocal()


    if db.query(Cartao).filter(Cartao.cpf == dados.cpf).first():
        raise HTTPException(status_code=400, detail="CPF já cadastrado.")

    score = random.randint(1, 999)

    if score < 300:
        aprovado = False
        limite = 0
    elif score < 600:
        aprovado = True
        limite = 1000
    elif score < 800:
        aprovado = True
        limite = max(1000, dados.renda * 0.5)
    elif score < 951:
        aprovado = True
        limite = dados.renda * 2
    else:
        aprovado = True
        limite = 1_000_000

    novo = Cartao(
        nome=dados.nome,
        cpf=dados.cpf,
        renda=dados.renda,
        score=score,
        aprovado=aprovado,
        limite=limite
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@app.delete("/cartoes/{cpf}")
def deletar_cartao(cpf: str):
    db = SessionLocal()
    item = db.query(Cartao).filter(Cartao.cpf == cpf).first()
    if not item:
        raise HTTPException(status_code=404, detail="Não encontrado.")
    db.delete(item)
    db.commit()
    return {"mensagem": f"Solicitação com CPF {cpf} removida."}

nest_asyncio.apply()


ngrok.set_auth_token("2zqmFBOpaNa2xQPFlQWJpZiNfq3_3x8Znee79FucEw6HBeUiy")


public_url = ngrok.connect(8000)
print("Sua API pública:", public_url)



