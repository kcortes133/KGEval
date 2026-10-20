"""Map KG node/edge type labels to Biolink Model (v4.4.5) categories/predicates.

Rules
- Nodes -> most specific Biolink category covering the KG's usage of the label.
- Edges with an explicit predicate -> the equivalent Biolink predicate; deprecated
  Biolink predicates (e.g. affects_X_of, increases/decreases_amount_or_activity_of)
  are collapsed to their current replacement (affects / regulates; direction and
  aspect would be Biolink qualifiers).
- Edges labelled only by node pair (e.g. "Gene-gene"): if the source KG uses one
  relation for that pair, map it directly; if it bundles several relations, map to
  the lowest common Biolink ancestor (LCA) of those relations, computed from the YAML.
- Internal/metadata relations with no biological meaning -> no_biolink_equivalent.
"""
import csv, yaml, sys

Y = yaml.safe_load(open("biolink.yaml"))
CLS, SLOTS = Y["classes"], Y["slots"]
NONE = "no_biolink_equivalent"

def s(n): return n.replace("_", " ")

def ancestors(p):
    out, cur = [], s(p)
    while cur:
        out.append(cur)
        cur = (SLOTS.get(cur) or {}).get("is_a")
    return out

def lca(*preds):
    chains = [ancestors(p) for p in preds]
    for a in chains[0]:
        if all(a in c for c in chains[1:]):
            return "related_to" if a == "related to at instance level" else a.replace(" ", "_")
    return "related_to"

N = {
 "Activity":"Activity","Agent":"Agent","Analytical Sample":"MaterialSample",
 "Anatomy/ Anatomical regions/ Anatomical Structure":"AnatomicalEntity",
 "Anatomical Entity":"AnatomicalEntity","Anatomy Cell Type":"Cell",
 "Antibody":"Protein","Antibody Panel":"InformationContentEntity",
 "Behavior":"Behavior","Behavioral Feature":"BehavioralFeature",
 "Biological Activity":"BiologicalProcessOrActivity","Biological Entity":"BiologicalEntity",
 "Biological Processes":"BiologicalProcess","Biological Sample":"MaterialSample",
 "Biomarker":"BiologicalEntity","Catalysts":"ChemicalEntity","Cells":"Cell",
 "Cell Lines":"CellLine","Cell types":"Cell","Cellular Components":"CellularComponent",
 "Cell Summary":"DatasetSummary","Chemicals / Chemical Entity/ Drugs":"ChemicalEntity",
 "Chemical Mixture":"ChemicalMixture","Chromosome":"NucleicAcidEntity",
 "Clinical Attribute":"ClinicalAttribute","Clinical Intervention":"ClinicalIntervention",
 "Clinical Variable":"ClinicalAttribute","Clinically Relevant Variable":"SequenceVariant",
 "Code":NONE,"Cofactors":"ChemicalEntity","Cohort":"Cohort",
 "Collision Summary":"InformationContentEntity","Complex":"MacromolecularComplex",
 "Compounds":"ChemicalEntity","Concept":"NamedThing","Corridor":"AnatomicalEntity",
 "Dataset":"Dataset","Definition":NONE,"Devices":"Device","Diseases":"Disease",
 "Domains":"ProteinDomain","Donor":"IndividualOrganism","Enhancer":"RegulatoryRegion",
 "Environmental Features":"EnvironmentalFeature","Environmental Processes":"EnvironmentalProcess",
 "Enzymatic Activity":"MolecularActivity","Epigenomic Features":"NucleicAcidEntity",
 "Event":"Event","Exon":"Exon","Experiment":"Study","Exposures":"ExposureEvent",
 "Extraction Site (Spatial Entity)":"AnatomicalEntity","Food":"Food",
 "FTU Illustration":"InformationContentEntity","FTU Illustration Node":"InformationContentEntity",
 "Functional Regions":"ProteinDomain","Genes":"Gene","Gene Family":"GeneFamily",
 "Genomic Entity":"NucleicAcidEntity","Genotype":"Genotype",
 "Geographical Location":"GeographicLocation","Gross Anatomical Structure":"GrossAnatomicalStructure",
 "GWAS Study":"Study","Information Content Entity":"InformationContentEntity",
 "Information Resource":"InformationContentEntity","Insulator":"RegulatoryRegion",
 "Known Variant":"SequenceVariant","Landmark":"PhysicalEntity","Life Stage":"LifeStage",
 "Macro Molecular Complex":"MacromolecularComplex","Material Sample":"MaterialSample",
 "Metabolite":"SmallMolecule","MicroRNA":"MicroRNA",
 "Millitome Extraction Site":"AnatomicalEntity","Modification":"PosttranslationalModification",
 "Modified Protein":"Protein","Molecular Activity":"MolecularActivity",
 "Molecular Entity":"MolecularEntity","Molecular Functions":"MolecularActivity",
 "Molecular Mixture":"MolecularMixture","Named Thing":"NamedThing",
 "Non Coding RNA Product":"NoncodingRNAProduct","Nucleic Acid Entity":"NucleicAcidEntity",
 "Nutrients":"ChemicalEntity","Organisms":"OrganismTaxon","Organism Taxon":"OrganismTaxon",
 "Organismal Entity":"OrganismalEntity","Pathalogical Processes":"PathologicalProcess",
 "Pathways":"Pathway","Peptides":"Polypeptide","Perturbagens":"ChemicalEntity",
 "Pharmacologic Classes":"ChemicalEntity","Phenomenon":"Phenomenon",
 "Phenotypes/ Effects/ Phenotypic Feature":"PhenotypicFeature","Physical Entity":"PhysicalEntity",
 "Physiological Processes":"PhysiologicalProcess","Polypeptide":"Polypeptide",
 "Population of Individual Organisms":"PopulationOfIndividualOrganisms","Procedure":"Procedure",
 "Project":"Study","Promoter":"RegulatoryRegion","Proteins":"Protein",
 "Protein Domains":"ProteinDomain","Protein Family":"ProteinFamily",
 "Protein Structure":"InformationContentEntity","Publications":"Publication",
 "Reactions":"MolecularActivity","Reference Organ":"AnatomicalEntity",
 "Reference Organ Part":"AnatomicalEntity","RNA Product":"RNAProduct","Semantic":NONE,
 "Sequences":"NucleicAcidEntity","Sequence Variant":"SequenceVariant",
 "Side Effects":"PhenotypicFeature","Small Molecules":"SmallMolecule",
 "Somatic Mutation":"SequenceVariant","Subject":"Case","Super Enhancer":"RegulatoryRegion",
 "Symptoms":"PhenotypicFeature","Term":NONE,"Tissues":"AnatomicalEntity",
 "Tssue Block (Sample)":"MaterialSample","Tissue Section (Sample)":"MaterialSample",
 "Transcript":"Transcript","Treatment":"Treatment","User":"Agent","Vaccines":"Drug",
 "Variants":"SequenceVariant","Vitamins":"ChemicalEntity","3D Structures":"NucleicAcidEntity",
}

MIX = {  # pair labels bundling several relations -> LCA
 "Anatomy-anatomy":("part_of","subclass_of"),
 "Biological process-biological process":("subclass_of","regulates"),
 "Cell-cell":("subclass_of","similar_to"),
 "Cell-disease":("model_of","associated_with"),
 "Cell-gene":("expresses","affects"),
 "Cell-pathway":("affects","associated_with"),
 "Cellular component-biological process":("participates_in","regulates"),
 "Chemical-disease":("treats","causes","preventative_for_condition"),
 "Chemical-gene":("physically_interacts_with","affects"),
 "Compound-compound":("chemically_similar_to","interacts_with"),
 "Compound-disease":("treats","contraindicated_in"),
 "Compound-gene":("physically_interacts_with","affects"),
 "Compound-protein":("physically_interacts_with","affects"),
 "Protein-compound":("physically_interacts_with","affects"),
 "Drug-protein":("physically_interacts_with","affects"),
 "ACTS_ON":("physically_interacts_with","affects"),
 "Disease-disease":("subclass_of","similar_to"),
 "Gene-gene":("interacts_with","coexpressed_with","regulates"),
 "Pathway-pathway":("part_of","subclass_of"),
 "Macromolecular Complex-biological process":("participates_in","regulates"),
 "Molecular Activity-biological process":("part_of","regulates"),
 "GeneFamily-biological process":("participates_in","regulates"),
 "GeneFamily-molecular activity":("enables","regulates"),
 "Protein-biological process":("participates_in","regulates"),
 "Pathway-biological process":("part_of","regulates"),
 "Pathway-chemical substance":("has_output","affects"),
 "Phenotypic Feature-disease":("phenotype_of","contributes_to"),
 "Reaction-compound":("has_input","has_output"),
 "Gene-ontologies (belong to)":("participates_in","enables","located_in"),
 "Non coding RNA-ontology":("participates_in","enables","located_in"),
 "Gene-transcriptional factors":("regulates","physically_interacts_with"),
}

E = {
 # explicit predicates
 "active_in":"active_in","actively_involved_in":"actively_involved_in",
 "acts_upstream_of":"acts_upstream_of",
 "acts_upstream_of_negative_effect":"acts_upstream_of_negative_effect",
 "acts_upstream_of_or_within":"acts_upstream_of_or_within",
 "acts_upstream_of_or_within_negative_effect":"acts_upstream_of_or_within_negative_effect",
 "acts_upstream_of_or_within_positive_effect":"acts_upstream_of_or_within_positive_effect",
 "acts_upstream_of_positive_effect":"acts_upstream_of_positive_effect",
 "affects":"affects","affects_response_to":"affects_sensitivity_to",
 "decreases_response_to":"decreases_sensitivity_to","increases_response_to":"increases_sensitivity_to",
 "ameliorates_condition":"ameliorates_condition","analogous_to":"similar_to",
 "applied_to_treat":"applied_to_treat",
 "associated_with_increased_likelihood_of":"associated_with_increased_likelihood_of",
 "capable_of":"capable_of","capable_of_part_of":"capable_of","catalyzes":"catalyzes",
 "causally_influenced_by":"affected_by","causally_influences":"affects",
 "caused_by":"caused_by","causes":"causes",
 "causes_or_contributes_to_condition":"contributes_to",
 "chemically_similar_to":"chemically_similar_to","coexists_with":"coexists_with",
 "coexpressed_with":"coexpressed_with","colocalizes_with":"colocalizes_with",
 "composed_primarily_of":"composed_primarily_of","connected_to":"related_to",
 "contraindicated_for":"contraindicated_in","contraindicated_in":"contraindicated_in",
 "contributes_to":"contributes_to","correlated_with":"correlated_with",
 "derives_from":"derives_from","develops_from":"develops_from","diagnoses":"diagnoses",
 "disease_has_basis_in":"disease_has_basis_in","disease_has_location":"disease_has_location",
 "disrupts":"disrupts","enables":"enables","EquivalentClass":"same_as","ExactMatch":"exact_match",
 "expressed_in":"expressed_in","function_of":"enabled_by",
 "gene_associated_with_condition":"gene_associated_with_condition",
 "gene_product_of":"gene_product_of","genetically_associated_with":"associated_with",
 "genetically_interacts_with":"genetically_interacts_with",
 "has_active_ingredient":"has_active_ingredient","has_adverse_event":"has_adverse_event",
 "has_biomarker":"has_biomarker","has_component":"has_part","has_function":"enables",
 "has_gene_product":"has_gene_product","has_input":"has_input","has_metabolite":"has_metabolite",
 "has_mode_of_inheritence":"has_mode_of_inheritance","has_output":"has_output",
 "has_part":"has_part","has_participant":"has_participant","Has_phenotype":"has_phenotype",
 "has_sequence_variant":"has_sequence_variant","homologous_to":"homologous_to",
 "in_complex_with":"in_complex_with","in_taxon":"in_taxon","interacts_with":"interacts_with",
 "is_active_in":"active_in","is_frameshift_variant_of":"is_frameshift_variant_of",
 "is_missense_variant_of":"is_missense_variant_of","is_nearby_variant_of":"is_nearby_variant_of",
 "is_non_coding_variant_of":"is_non_coding_variant_of",
 "is_nonsense_variant_of":"is_nonsense_variant_of","is_sequence_variant_of":"is_sequence_variant_of",
 "is_splice_site_variant_of":"is_splice_site_variant_of",
 "is_synonymous_variant_of":"is_synonymous_variant_of",
 "is_substance_that_treats":"treats","is_treated_by_substance":"treated_by",
 "LOCATED_IN":"located_in","location_of":"location_of","manifestation_of":"manifestation_of",
 "model_of":"model_of","molecularly_interacts_with":"physically_interacts_with",
 "negatively_correlated_with":"negatively_correlated_with","occurs_in":"occurs_in",
 "orthologous_to":"orthologous_to","overlaps":"overlaps","part_of":"part_of",
 "PARTICIPATES_IN":"participates_in","phenotype_of":"phenotype_of",
 "physically_interacts_with":"physically_interacts_with",
 "positively_correlated_with":"positively_correlated_with","positively_regulates":"regulates",
 "precedes":"precedes","predisposes_to_condition":"predisposes_to_condition",
 "preventative_for_condition":"preventative_for_condition","prevents":"preventative_for_condition",
 "produces":"produces","realized_in_response_to":"affected_by","regulates":"regulates",
 "related_to":"related_to","responsible_for":"contributes_to",
 "ribosomal_translation_of":"translation_of","ribosomally_translates_to":"translates_to",
 "same_as":"same_as","similar_to":"similar_to","Subclass_of":"subclass_of",
 "superclass_of":"superclass_of","target_for":"target_for",
 "temporarily_related_to":"temporally_related_to","transcribed_from":"transcribed_from",
 "transcribed_to":"transcribed_to","transports":"affects","treats":"treats",
 "treats_or_applied_or_studied_to_treat":"treats_or_applied_or_studied_to_treat",
 "upstream_of":"acts_upstream_of","variant_of":"is_sequence_variant_of",
 # Clinical KG
 "ANNOTATED_IN_PATHWAY":"participates_in","ASSOCIATED_WITH":"associated_with",
 "ASSOCIATED_WITH_INTEGRATED":"associated_with","BELONGS_TO_PROTEIN":"part_of",
 "BELONGS_TO_SUBJECT":"derives_from","COMPILED_INTERACTS_WITH":"interacts_with",
 "COMPILED_TARGETS":"physically_interacts_with","CURATED_TARGETS":"physically_interacts_with",
 "CURATED_AFFECTS_INTERACTION_WITH":"affects","CURATED_INTERACTS_WITH":"interacts_with",
 "DETECTED_IN_PATHOLOGY_SAMPLE":"associated_with","FOUND_IN_PROTEIN":"part_of",
 "FROM_TISSUE":"derives_from","HAS_CLINICAL_STATE":"related_to",
 "HAS_CONTENT":"has_food_component","HAS_DISEASE":"has_phenotype",
 "HAS_ENROLLED":"has_participant","HAS_MODIFICATION":"related_to",
 "HAS_MODIFIED_SITE":"related_to","HAS_PARENT":"subclass_of",
 "HAS_QUANTIFIED_CLINICAL":"related_to","HAS_QUANTIFIED_MODIFIED_PROTEIN":"related_to",
 "HAS_QUANTIFIED_PEPTIDE":"related_to","HAS_QUANTIFIED_PROTEIN":"related_to",
 "HAS_SIDE_EFFECT":"has_side_effect","HAS_STRUCTURE":"related_to",
 "IS_A_KNOWN_VARIANT":"same_as","IS_BIOMARKER_OF_DISEASE":"biomarker_for",
 "IS_INDICATED_FOR":"treats","IS_RESPONSIBLE_FOR":"related_to",
 "IS_SUBSTRATE_OF":"is_substrate_of","IS_SUBUNIT_OF":"part_of",
 "MENTIONED_IN_PUBLICATION":"mentioned_by","PUBLISHED_IN":"related_to",
 "SPLITTED_INTO":"derives_into","STUDIES_DISEASE":"related_to","STUDIES_TISSUE":"related_to",
 "TARGETS_CLINICALLY_RELEVANT_VARIANT":"response_associated_with",
 "TRANSCRIBED_INTO":"transcribed_to","TRANSLATED_INTO":"translates_to",
 "VARIANT_FOUND_IN_CHROMOSOME":"has_sequence_location",
 "VARIANT_FOUND_IN_GENE":"is_sequence_variant_of","VARIANT_FOUND_IN_PROTEIN":"related_to",
 "VARIANT_IS_CLINICALLY_RELEVANT":"same_as",
 # NCATS GARD internal relations
 "I_Code":NONE,"N_Name":NONE,"PAYLOAD":NONE,"I_GENE":"related_to","R_rel":"related_to",
 # pair-labelled edges with a single documented relation
 "Anatomical structure-anatomical structure":"part_of","AnatomyCellType-anatomy":"part_of",
 "AnatomyCellType-CellType":"subclass_of","AnatomyCellType-gene":"expresses",
 "Anatomy-gene":"expresses","Anatomy-protein (absent)":"expresses",
 "Anatomy-protein (present)":"expresses","Antibody panel-antibody":"has_member",
 "Biological process-disease":"contributes_to","Biological process-organism taxon":"in_taxon",
 "Biological process-protein":"has_participant","Biomarker-cell type":"expressed_in",
 "Cell-biological process":"participates_in","Cell-compound":"associated_with_sensitivity_to",
 "Cellular component-cellular component":"subclass_of",
 "Cellular component-organism taxon":"in_taxon","Cellular component-protein":"location_of",
 "Cell/tissue ontology-cell/tissue ontology":"subclass_of",
 "Cell Summary-biomarker":"mentions","Cell Summary-cell type":"mentions",
 "CellType-anatomical structure":"located_in","Chemical-biological process":"affects",
 "Chemical-chemical":"interacts_with","Compound-chemical entity":"subclass_of",
 "Compound-disease (causal)":"causes","Compound-disease (palliates)":"ameliorates_condition",
 "Compound-pharmacologic class":"subclass_of","Compound-protein domain":"physically_interacts_with",
 "Compound-side effect":"has_side_effect","Dataset-cell summary":"derives_into",
 "Dataset-tissue section":"derives_from","Disease-anatomy":"disease_has_location",
 "Disease-gene":"condition_associated_with_gene","Disease-phenotype (negative)":"has_phenotype",
 "Disease-phenotype (positive)":"has_phenotype","Disease-protein":"condition_associated_with_gene",
 "Disease-symptom":"has_phenotype","Domain-domain (protein)":"interacts_with",
 "Donor-tissue block":"derives_into","Drug-disease (contraindication)":"contraindicated_in",
 "Drug-disease (indication)":"treats","Drug-disease (off-label use)":"applied_to_treat",
 "Drug-drug":"interacts_with","Drug-gene family":"affects","Drug-phenotype":"has_side_effect",
 "EC-EC":"subclass_of","Entity-genomic sequence (locate at)":"has_sequence_location",
 "Enhancer-gene":"regulates","Exposure-biological process":"affects",
 "Exposure-cellular component":"affects","Exposure-disease":"associated_with",
 "Exposure-exposure":"subclass_of","Exposure-molecular function":"affects",
 "Exposure-protein":"affects","Extraction Site-anatomical structure":"overlaps",
 "Extraction Site-collision summary":"mentioned_by","Extraction Site-corridor":"related_to",
 "Extraction Site-reference organ":"located_in","Enzymatic activity-EC":"subclass_of",
 "Enzymatic activity–Metabolic reaction":"catalyzes","Food-compund":"has_food_component",
 "Food-food":"subclass_of","FTU Illustration-FTU Illustration node":"has_part",
 "gene-anatomy":"expressed_in","Gene-biological process":"participates_in",
 "Gene-cellular component":"located_in",
 "Gene-compound (upregulation_sensitizes)":"increases_sensitivity_to",
 "Gene-disease":"gene_associated_with_condition","Genomic sequence-genomic sequence":"overlaps",
 "Gene-molecular function":"enables","Gene-ontologies (express in)":"expressed_in",
 "Gene-pathway":"participates_in","Gene-protein":"has_gene_product",
 "gene-symptom":"gene_associated_with_condition","Gene-tissue":"expressed_in",
 "Gene-transcript":"transcribed_to","Gene ontology-gene ontology":"subclass_of",
 "Gene product-gene":"gene_product_of",
 "Gross Anatomical Structure-disease":"location_of_disease",
 "Gross Anatomical Structure-phenotypic feature":"location_of",
 "Knocked-out gene-gene":"affects","Landmark-reference organ part":"located_in",
 "Millitome Extraction Site-reference organ":"located_in",
 "Molecular Activity-organism taxon":"in_taxon",
 "Molecular function-molecular function":"subclass_of","Molecular function-protein":"enabled_by",
 "Organism-disease":"causes","Organism-organism":"subclass_of","Organism-protein":"taxon_of",
 "Organism Taxon-disease":"causes","Organism Taxon-phenotypic feature":"causes",
 "Overexpressed gene-gene":"affects","Pathway group- pathway group":"part_of",
 "Perturbagen-cell":"affects","Perturbagen-gene":"affects",
 "Pharmacologic class-compound":"superclass_of",
 "Pharmacologic class-pharmacologic class":"subclass_of",
 "Phenotype-phenotype":"subclass_of","Phenotype-protein":"associated_with",
 "Protein-cellLine":"expressed_in","Protein-cellType":"expressed_in",
 "Protein-chemical substance":"affects","Protein-disease":"gene_associated_with_condition",
 "Protein-protein":"interacts_with","ProteinDomain-protein":"part_of",
 "ProteinDomain-proteindomain":"interacts_with","ProteinDomain-proteinfamily":"subclass_of",
 "Protein-Enzymatic activity":"enables","Protein-pathway group":"participates_in",
 "Sequence variants-gene":"is_sequence_variant_of","Tissue-disease":"location_of_disease",
 "Tissue-tissue":"subclass_of","Tissue Block-extraction site":"located_in",
 "Tissue Block-millitome extraction site":"located_in","Tissue Block-tissue section":"derives_into",
 "Transcript-exons":"has_part","Transcript-protein":"translates_to",
 "Variant-gene/ontologies":"is_sequence_variant_of",
}
# deprecated affects_X_of / increases_X_of / decreases_X_of -> affects (+ aspect/direction qualifiers)
for pre in ("affects_", "increases_", "decreases_"):
    for asp in ("abundance","activity","degradation","expression","localization",
                "metabolic_processing","molecular_modification","mutation_rate",
                "secretion","splicing","stability","synthesis","transport"):
        E.setdefault(f"{pre}{asp}_of", "affects")
for k, v in MIX.items():
    E[k] = lca(*v)

def camel_to_space(c):
    import re
    if c == "RNAProduct": return "RNA product"
    if c == "NoncodingRNAProduct": return "noncoding RNA product"
    if c == "MicroRNA": return "microRNA"
    return re.sub(r"(?<!^)(?=[A-Z])", " ", c).lower()

errors = []
def check_node(v):
    if v != NONE and camel_to_space(v) not in CLS: errors.append(("node", v))
def check_edge(v):
    if v == NONE: return
    sl = SLOTS.get(s(v))
    if sl is None: errors.append(("edge-missing", v))
    elif sl.get("deprecated"): errors.append(("edge-deprecated", v))

def run(infile, col, table, check, outfile, fmt):
    rows = list(csv.DictReader(open(infile, encoding="utf-8-sig")))
    with open(outfile, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["original", "biolink_mapping"])
        for r in rows:
            o = r[col]
            if o not in table: errors.append(("unmapped", o)); continue
            v = table[o]; check(v)
            w.writerow([o, v if v == NONE else fmt(v)])
    return len(rows)

import os
os.makedirs("/mnt/user-data/outputs", exist_ok=True)
nn = run("/mnt/user-data/uploads/Node_Types.csv","Node Types",N,check_node,
         "/mnt/user-data/outputs/node_type_biolink_mapping.csv", lambda v:"biolink:"+v)
ne = run("/mnt/user-data/uploads/Edge_Types.csv","Edge Types",E,check_edge,
         "/mnt/user-data/outputs/edge_type_biolink_mapping.csv", lambda v:"biolink:"+v)
print("nodes", nn, "edges", ne, "biolink", Y["version"])
print("ERRORS:", errors)
print({k: E[k] for k in MIX})
