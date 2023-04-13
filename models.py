# from sqlalchemy import create_engine, ForeignKey
# from sqlalchemy import db.Column
# from sqlalchemy import Table
# from sqlalchemy import ForeignKey
# from sqlalchemy import db.Integer
# from sqlalchemy import db.String
# from sqlalchemy import db.Float
# from sqlalchemy.orm import scoped_session
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_db.Column
# from sqlalchemy.orm import backref
# from sqlalchemy.orm import Declarativedb.Model
# from sqlalchemy.orm import relationship
# from sqlalchemy.orm import Session
# from sqlalchemy.orm import declarative_db.Model
# from sqlalchemy import select

from vui import db

consequences = {value:key.strip() for value, key in enumerate(open("consequences.txt", "r").readlines())}

def bitvector_consequence(bitvector):
    ret = []
    i = 0
    while bitvector != 0:
        if bitvector & 1 == 1:
            ret.append(consequences[i])
        i+=1
        bitvector = bitvector >> 1
    return ret

impacts = {
    0:"MODIFIER",
    1:"LOW",
    2:"MODERATE",
    3:"HIGH",
}

def bitvector_impacts(bitvector):
    ret = []
    i = 0
    while bitvector != 0:
        if bitvector & 1 == 1:
            ret.append(impacts[i])
        i+=1
        bitvector = bitvector >> 1
    return ret

class Sample_Has_Variant(db.Model):
    __tablename__ = "sample_has_variant"
    variant_id = db.Column(db.Integer, db.ForeignKey("variants.id"), primary_key=True)
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"), primary_key=True)
    genotype = db.Column(db.Integer, index=True)
    dp = db.Column(db.Integer, index=True)
    sample = db.relationship("Sample", back_populates="variants")
    variant = db.relationship("Variant", back_populates="samples")


class Variant(db.Model):
    __tablename__ = "variants"
    id = db.Column(db.Integer, primary_key=True)
    chr = db.Column(db.String, index=True)
    pos = db.Column(db.Integer, index=True)
    ref = db.Column(db.String, index=True)
    alt = db.Column(db.String, index=True)
    qual = db.Column(db.Float, index=True)
    mq = db.Column(db.Integer, index=True)
    ac = db.Column(db.Integer, index=True)
    af = db.Column(db.Float, index=True)
    an = db.Column(db.Integer, index=True)
    nhomalt = db.Column(db.Integer, index=True)
    consequences = db.Column(db.Integer)
    impacts = db.Column(db.Integer)
    samples = db.relationship("Sample_Has_Variant", back_populates="variant")
    ann = db.relationship("Annotation", backref="variant")

    def to_dict(self):
        return {
            'chr': self.chr,
            'pos': self.pos,
            'ref': self.ref,
            'alt': self.alt,
            'qual': self.qual,
            'impacts': bitvector_impacts(self.impacts),
            'ac': self.ac,
            'an': self.an,
            'af': self.af,
            'nhomalt': self.nhomalt,
            'consequences': bitvector_consequence(self.consequences),
        }

class Annotation(db.Model):
    __tablename__ = "annotations"
    id = db.Column(db.Integer, primary_key=True)
    variant_id = db.Column(db.Integer, db.ForeignKey("variants.id"))
    transcript = db.Column(db.Integer, index=True)
    consequence = db.Column(db.String, index=True)
    impact = db.Column(db.String, index=True)
    symbol = db.Column(db.String, index=True)
    gene = db.Column(db.Integer, index=True)
    feature_type = db.Column(db.String, index=True)
    biotype = db.Column(db.String, index=True)
    exon = db.Column(db.Integer, index=True)
    intron = db.Column(db.Integer, index=True)
    hgvsc = db.Column(db.String, index=True)
    hgvsp = db.Column(db.String, index=True)
    cdna_position = db.Column(db.Integer, index=True)
    cds_position = db.Column(db.Integer, index=True)
    protein_position = db.Column(db.Integer, index=True)
    amino_acids = db.Column(db.String, index=True)
    codons = db.Column(db.String, index=True)
    existing_variation = db.Column(db.String, index=True)
    distance = db.Column(db.Integer, index=True)
    strand = db.Column(db.Integer, index=True)
    flags = db.Column(db.String, index=True)
    symbol_source = db.Column(db.String, index=True)
    hgnc_id = db.Column(db.Integer, index=True)


class Sample(db.Model):
    __tablename__ = "samples"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    variants = db.relationship("Sample_Has_Variant", back_populates="sample")