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


from pysam import VariantFile

if os.path.exists("test.sqlite"):
    os.remove("test.sqlite")
engine = create_engine("sqlite:///test.sqlite")

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
    consequences = Column(Integer)
    impacts = Column(Integer)


class Annotation(Base):
    __tablename__ = "annotations"
    id = Column(Integer, primary_key=True)
    variant_id = Column(Integer, ForeignKey("variants.id"))
    transcript = Column(Integer, index=True)
    consequence = Column(String, index=True)
    impact = Column(String, index=True)
    symbol = Column(String, index=True)
    gene = Column(Integer, index=True)
    feature_type = Column(String, index=True)
    biotype = Column(String, index=True)
    exon = Column(Integer, index=True)
    intron = Column(Integer, index=True)
    hgvsc = Column(String, index=True)
    hgvsp = Column(String, index=True)
    cdna_position = Column(Integer, index=True)
    cds_position = Column(Integer, index=True)
    protein_position = Column(Integer, index=True)
    amino_acids = Column(String, index=True)
    codons = Column(String, index=True)
    existing_variation = Column(String, index=True)
    distance = Column(Integer, index=True)
    strand = Column(Integer, index=True)
    flags = Column(String, index=True)
    symbol_source = Column(String, index=True)
    hgnc_id = Column(Integer, index=True)


class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    variants = relationship("Sample_Has_Variant", back_populates="sample")


Base.metadata.create_all(bind=engine)


# open consequences enum
consequences = {key.strip():value for value, key in enumerate(open("consequences.txt", "r").readlines())}

def consequence_bitvector(consequence):
    return sum(2**consequences[c] for c in consequence.split("&"))

impacts = {
    "MODIFIER":0,
    "LOW":1,
    "MODERATE":2,
    "HIGH":3,
}

with VariantFile("variants.no_intergenic.bcf") as f:
    ann_format = list(
        map(str.lower, f.header.info["CSQ"].description.rsplit(" ", 1)[-1].split("|"))
    )

    print("insert samples", file=sys.stderr)
    objects = [
        Sample(id=sample_id, name=str(s))
        for sample_id, s in enumerate(f.header.samples)
    ]
    db_session.bulk_save_objects(objects)

    print("insert variants", file=sys.stderr)
    samples = [str(s) for s in f.header.samples]
    objects = []
    annotation_id = 0
    for variant_id, variant in enumerate(f):
        # if variant_id == 25000:
        #     break

        # create variant
        info = variant.info
        if variant_id % 10000 == 0:
            print(variant_id)
            db_session.bulk_save_objects(objects)
            objects = []

        # create relation of sample - variant
        for sample_id, s in enumerate(samples):
            format = variant.samples[s]
            gt = format["GT"]
            if gt == (None,):  # dont write sample, if it doesn't own the variant
                continue
            genotype = sum(2**i * x for i, x in enumerate(gt))
            if genotype == 0:  # dont write sample, if it doesn't own the variant
                continue
            objects.append(
                Sample_Has_Variant(
                    sample_id=sample_id,
                    variant_id=variant_id,
                    genotype=genotype,
                    dp=format.get("DP", None) or format.get("DPI", None),
                ),
            )

        all_consequences = 0
        all_impacts = 0

        # add annotations
        for a in info["CSQ"]:
            ann = {key: value for key, value in zip(ann_format, a.split("|"))}
            consequence_bits = consequence_bitvector(ann["consequence"])
            all_consequences |= consequence_bits
            impact_bit = 2**impacts[ann["impact"]]
            all_impacts |= impact_bit
            hgnc_id = int(ann["hgnc_id"].removeprefix("HGNC:")) if ann["hgnc_id"] else None
            assert ann["feature_type"]=="Transcript"
            # print(ann["biotype"])
            objects.append(
                Annotation(
                    id=annotation_id,
                    variant_id=variant_id,
                    transcript=int(ann["feature"].removeprefix("ENST")),
                    consequence=consequence_bits,
                    impact=ann["impact"],
                    symbol=ann["symbol"],
                    gene=int(ann["gene"].removeprefix("ENSG")),
                    # feature_type=ann["feature_type"],
                    biotype=ann["biotype"],
                    exon=ann["exon"],
                    intron=ann["intron"],
                    hgvsc=ann["hgvsc"],
                    hgvsp=ann["hgvsp"],
                    cdna_position=ann["cdna_position"],
                    cds_position=ann["cds_position"],
                    protein_position=ann["protein_position"],
                    amino_acids=ann["amino_acids"],
                    codons=ann["codons"],
                    existing_variation=ann["existing_variation"],
                    distance=ann["distance"],
                    strand=ann["strand"],
                    flags=ann["flags"],
                    symbol_source=ann["symbol_source"],
                    hgnc_id=hgnc_id,
                ),
            )
            annotation_id += 1

        # add variant
        objects.append(
            Variant(
                id=variant_id,
                chr=variant.chrom,
                pos=variant.pos,
                ref=variant.alts[0],
                alt=variant.ref,
                qual=variant.qual,
                consequences=all_consequences,
                impacts=all_impacts,
                mq=info.get("MQ", None),
                ac=info.get("AC", (None,))[0],
                af=info.get("AF", (None,))[0],
                an=info.get("AN", None),
                nhomalt=info.get("nhomalt", (None,))[0],
            ),
        )
    db_session.bulk_save_objects(objects)

db_session.commit()
db_session.flush()
db_session.close()
