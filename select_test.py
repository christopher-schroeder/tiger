from __future__ import annotations
from typing import List

import sys
import os

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import backref
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy.orm import declarative_base
from sqlalchemy import select

from pysam import VariantFile

engine = create_engine("sqlite:///variants.no_intergenic.sqlite")

db_session = scoped_session(sessionmaker(bind=engine, autoflush=True))

Base = declarative_base()


class Sample_Has_Variant(Base):
    __tablename__ = "sample_has_variant"
    variant_id = Column(Integer, ForeignKey("variants.id"), primary_key=True)
    sample_id = Column(Integer, ForeignKey("samples.id"), primary_key=True)
    genotype = Column(Integer, index=True)
    dp = Column(Integer, index=True)
    sample = relationship("Sample", back_populates="variants")
    variant = relationship("Variant", back_populates="samples")


class Variant(Base):
    __tablename__ = "variants"
    id = Column(Integer, primary_key=True)
    chr = Column(String, index=True)
    pos = Column(Integer, index=True)
    ref = Column(String, index=True)
    alt = Column(String, index=True)
    qual = Column(Float, index=True)
    samples = relationship("Sample_Has_Variant", back_populates="variant")
    ann = relationship("Annotation", backref="variant")
    mq = Column(Integer, index=True)
    ac = Column(Integer, index=True)
    af = Column(Float, index=True)
    an = Column(Integer, index=True)
    nhomalt = Column(Integer, index=True)


class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("variants.id"))
    transcript = Column(String, index=True)
    consequence = Column(String, index=True)
    impact = Column(String, index=True)
    symbol = Column(String, index=True)
    gene = Column(String, index=True)
    feature_type = Column(String, index=True)
    biotype = Column(String, index=True)
    exon = Column(String, index=True)
    intron = Column(String, index=True)
    hgvsc = Column(String, index=True)
    hgvsp = Column(String, index=True)
    cdna_position = Column(String, index=True)
    protein_position = Column(String, index=True)
    amino_acids = Column(String, index=True)
    codons = Column(String, index=True)
    existing_variation = Column(String, index=True)
    distance = Column(String, index=True)
    strand = Column(String, index=True)
    flags = Column(String, index=True)
    symbol_source = Column(String, index=True)
    hgnc_id = Column(String, index=True)


class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    variants = relationship("Sample_Has_Variant", back_populates="sample")


stmt = db_session.query(Variant).paginate(10,100,False)
for v in db_session.execute(stmt):
    print(v[0].chr)