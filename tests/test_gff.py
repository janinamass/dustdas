import pytest
from dustdas import gffhelper
import os
dir = os.path.dirname(__file__)


@pytest.mark.parametrize("gff, expected", [
    (os.path.join(dir,'test.gff3'),['gff-version 3.2.1', 'sequence-region ctg123 1 1497228']),
    (os.path.join(dir,'test2.gff3'),['gff-version 3.2.1', 'sequence-region ctg1234 1 1497228'])
    ])
def test_metadata(gff, expected):
    g = gffhelper.GFFFile(gff)
    assert g.path == gff
    assert g.metadata == expected


@pytest.mark.parametrize("gff, expected", [
    (os.path.join(dir,'test.gff3'),'ctg123'),
    (os.path.join(dir,'test2.gff3'),'ctg1234')
    ])
def test_seqid(gff, expected):
    g = gffhelper.GFFFile(gff)
    for o in g.get_gff_objects():
        assert o.seqid == expected

@pytest.mark.parametrize("gff, expected", [
    (os.path.join(dir,'test.gff3'),'.'),
    (os.path.join(dir,'test2.gff3'),'.')
    ])
def test_source(gff, expected):
    g = gffhelper.GFFFile(gff)
    for o in g.get_gff_objects():
        assert o.source == expected


@pytest.mark.parametrize("gff, index, expected", [
    (os.path.join(dir,'test.gff3'),0,'gene'),
    (os.path.join(dir,'test.gff3'),1, 'TF_binding_site'),
    (os.path.join(dir,'test.gff3'),2, 'mRNA'),
    (os.path.join(dir,'test.gff3'),4, 'mRNA'),
    (os.path.join(dir,'test.gff3'),22, 'CDS'),
    (os.path.join(dir,'test3.gff3'),0, 'mRNA'),
    (os.path.join(dir,'test3.gff3'),1, 'exon')
    ])
def test_type(gff, index, expected):
    g = gffhelper.GFFFile(gff)
    objs = list(g.get_gff_objects())
    assert objs[index].type == expected

@pytest.mark.parametrize("gff, index, expected_start, expected_end", [
    (os.path.join(dir,'test.gff3'),0, 1000, 9000),
    (os.path.join(dir,'test.gff3'),1, 1000, 1012),
    (os.path.join(dir,'test.gff3'),2, 1050, 9000),
    (os.path.join(dir,'test.gff3'),4, 1300, 9000),
    (os.path.join(dir,'test.gff3'),22, 7000, 7600),
    (os.path.join(dir,'test3.gff3'),0, 1300, 9000),
    (os.path.join(dir,'test3.gff3'),1, 1300, 1500)
    ])
def test_start_end(gff, index, expected_start, expected_end):
    g = gffhelper.GFFFile(gff)
    objs = list(g.get_gff_objects())
    assert int(objs[index].start) == expected_start
    assert int(objs[index].end) == expected_end


@pytest.mark.parametrize("gff, index, expected_score, expected_strand, expected_phase", [
    (os.path.join(dir,'test.gff3'),0, ".","+", "."),
    (os.path.join(dir,'test.gff3'),1, ".","+", "."),
    (os.path.join(dir,'test.gff3'),2, ".","+", "."),
    (os.path.join(dir,'test.gff3'),4, ".","+", "."),
    (os.path.join(dir,'test.gff3'),20, ".","+", "0"),
    (os.path.join(dir,'test.gff3'),22, ".","+", "1"),
    (os.path.join(dir,'test3.gff3'),1, 1e-2,"+", "."),
    (os.path.join(dir,'test3.gff3'),2, 0.9, "+", "."),
    (os.path.join(dir,'test3.gff3'),3, 0.000001, "+", ".")
    ])
def test_score(gff, index, expected_score, expected_strand, expected_phase):
    g = gffhelper.GFFFile(gff)
    objs = list(g.get_gff_objects())
    assert objs[index].score == expected_score
    assert objs[index].strand == expected_strand
    assert objs[index].phase == expected_phase


@pytest.mark.parametrize("gff, index, expected_attributes", [
    (os.path.join(dir,'test.gff3'),0, [{"tag":"ID", "value":"gene00001"},{"tag":"Name" , "value":"EDEN"}]),
    (os.path.join(dir,'test.gff3'),1, [{"tag":"ID", "value":"tfbs00001"},{"tag":"Parent" , "value":"gene00001"}]),
    (os.path.join(dir,'test.gff3'),6, [{"tag":"ID", "value":"exon00002"},{"tag":"Parent" , "value":"mRNA00001,mRNA00002"}]),
    (os.path.join(dir,'test.gff3'),9, [{"tag":"ID", "value":"exon00005"},{"tag":"Parent" , "value":"mRNA00001,mRNA00002,mRNA00003"}])
])
def test_attributes(gff, index, expected_attributes ):
    g = gffhelper.GFFFile(gff)
    objs = list(g.get_gff_objects())
    for e in expected_attributes:
        vals = [a.value for a in objs[index].attributes if a.tag == e["tag"]]
        assert vals == [list(e["value"].split(","))]


# attributes
# parent, alias, note, dbxref, ontology_term attributes can have multiple values separated by comma
@pytest.mark.parametrize("gff, index, expected_id, expected_alias, expected_note", [
   # (os.path.join(dir,'test.gff3'),0, [{"tag":"ID", "value":"gene00001"},{"tag":"Name" , "value":"EDEN"}]),
    (os.path.join(dir,'test.gff3'),1, "tfbs00001", None, None),
    (os.path.join(dir,'test3.gff3'),3, "exon00003",["Blah"],["ABC","DEF"]),
])
def test_attrib_id_alias_note_(gff, index, expected_id, expected_alias, expected_note):
    g = gffhelper.GFFFile(gff)
    o= list(g.get_gff_objects())[index]
    i = o.get_ID()
    a = o.get_Alias()
    print(a)
    n = o.get_Note()
    assert i == expected_id
    try:
        assert a == expected_alias
    except AssertionError:
        try:
            assert  a == []
        except AssertionError:
            raise AssertionError
    try:
        assert n == expected_note
    except AssertionError:
        try:
            assert n == []
        except AssertionError:
            raise AssertionError

@pytest.mark.parametrize("gff, index, expected_Parent", [
   # (os.path.join(dir,'test.gff3'),0, [{"tag":"ID", "value":"gene00001"},{"tag":"Name" , "value":"EDEN"}]),
    (os.path.join(dir,'test.gff3'),1, ["gene00001"]),
    (os.path.join(dir,'test.gff3'),6, ["mRNA00001", "mRNA00002"]),
    (os.path.join(dir,'test.gff3'),9, ["mRNA00001", "mRNA00002","mRNA00003"])
])
def test_attrib_parent(gff, index, expected_Parent):
    g = gffhelper.GFFFile(gff)
    objs = list(g.get_gff_objects())
    p = objs[index].get_Parent()
    assert p == expected_Parent


#def test_attrib_target():
#    #TODO The format of the value is "target_id start end [strand]", where strand is optional and may be "+" or "-".
#    pass


#def test_attrib_gap():
# TODO ??http://cvsweb.sanger.ac.uk/cgi-bin/cvsweb.cgi/exonerate?cvsroot=Ensembl is down and reference go in cirles -- hooray
#    pass


#def test_attrib_derives_from():
# TODO ??
#    pass

@pytest.mark.parametrize("gff, index, expected_Ontology_term, expected_Dbxref", [
   # (os.path.join(dir,'test.gff3'),0, [{"tag":"ID", "value":"gene00001"},{"tag":"Name" , "value":"EDEN"}]),
    (os.path.join(dir,'test3.gff3'),6, ["GO:0046703"], ["EMBL:AA816246","NCBI_gi:10727410"]),
])
def test_attrib_ontology_term(gff, index, expected_Ontology_term, expected_Dbxref):
    g = gffhelper.GFFFile(gff)
    o = list(g.get_gff_objects())[index]
    d = [x.strip('"') for x in o.get_Dbxref()]
    ot = [x.strip('"') for x in o.get_Ontology_term()]
    assert d == expected_Dbxref
    assert ot == expected_Ontology_term
    pass

@pytest.mark.parametrize("gff, index, expected_Is_circular", [
    (os.path.join(dir,'test3.gff3'),9, ["true"]),
])
def test_attrib_is_circular(gff, index, expected_Is_circular):
    g = gffhelper.GFFFile(gff)
    o = list(g.get_gff_objects())[index]
    c = o.get_Is_circular()
    assert c == expected_Is_circular


@pytest.mark.parametrize("gff, expected", [
    (os.path.join(dir,'test_avail.gff3'),{'exon': 5, 'mRNA': 2, 'region': 1, 'translated_nucleotide_match': 2}),
    (os.path.join(dir,'test.gff3'),{'exon': 5, 'CDS': 13, 'gene': 1, 'mRNA': 3, 'TF_binding_site': 1}),
])
def test_available_types(gff, expected):
    g = gffhelper.GFFFile(gff)
    t = g.get_available_types()
    print(t)
    assert  t == expected

@pytest.mark.parametrize("gff, expected", [
    (os.path.join(dir,'test.gff3'),{'gene00001': ['mRNA00001','mRNA00002','mRNA00003'],
                                    'mRNA00001': [
                                        ['exon00002', 'exon00003', 'exon00004', 'exon00005'],
                                        ['cds00001', 'cds00001', 'cds00001', 'cds00001']
                                    ],
                                    'mRNA00002': [
                                        ['exon00002', 'exon00004', 'exon00005'],
                                        ['cds00002', 'cds00002', 'cds00002']
                                    ],
                                    'mRNA00003':[
                                        ['exon00001', 'exon00003', 'exon00004', 'exon00005'],
                                        ['cds00003', 'cds00003', 'cds00003', 'cds00004', 'cds00004', 'cds00004']
                                    ]
                                    }),
])
def test_mrna_cds(gff, expected):
    """find all cds that belong to mrna"""
    genes = []
    mrnas = []
    cds = []
    exons = []
    res = {}
    gf = gffhelper.GFFFile(gff)
    for o in  gf.get_gff_objects():
        if o.type == "gene":
            genes.append(o)
        if o.type == "mRNA":
            mrnas.append(o)
        if o.type == "CDS":
            cds.append(o)
        if o.type == "exon":
            exons.append(o)

    for g in genes:
        #print("gene:", g)
        mg = [m.get_ID() for m in mrnas if g.get_ID() in m.get_Parent()]
        res[g.get_ID()] = mg
        for m in mg:
            emg = [e.get_ID() for e in exons if m in e.get_Parent()]
            res[m] = [emg]
            cmg = [c.get_ID() for c in cds if m in c.get_Parent()]
            #print(m,"\n", emg,"\n", cmg, "\n\n")
            res[m].append(cmg)
    print(res)
    assert res == expected


def test_proteinconversion():
    """"""
    pass

