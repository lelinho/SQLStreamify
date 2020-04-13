#!/usr/bin/env python

from jsondiff import diff


um = """[{"itemid": 53939, "clock": 1586818055, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 585528343}, {"itemid": 53939, "clock": 1586818115, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 412763663}, {"itemid": 53939, "clock": 1586818175, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 616522704}, {"itemid": 53939, "clock": 1586818235, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 594658699}, {"itemid": 53939, "clock": 1586818295, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 763118918}, {"itemid": 53939, "clock": 1586818355, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 596392015}]"""

outro = """[{"itemid": 53939, "clock": 1586818055, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 585528343}, {"itemid": 53939, "clock": 1586818115, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 412763663}, {"itemid": 53939, "clock": 1586818175, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 616522704}, {"itemid": 53939, "clock": 1586818235, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 594658699}, {"itemid": 53939, "clock": 1586818295, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 763118918}, {"itemid": 53939, "clock": 1586818355, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 596392015}, {"itemid": 53939, "clock": 1586818415, "value": "Link_Bloco_de_Aulas_1_POSMAC_187.167", "ns": 699185996}]"""

dif = diff(um, outro, load=True, dump=True)
print(dif)
