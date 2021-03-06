# Uniprot to string mapping https://string-db.org/mapping_files/uniprot/human.uniprot_2_string.2018.tsv.gz
# String PPI dataset https://stringdb-static.org/download/protein.actions.v11.0/9606.protein.actions.v11.0.txt.gz
# Columns definition http://www.string-db.org/help/faq/#what-does-the-columns-in-proteinsactions-file-mean

import pandas as pd
import wget
import os
import sys
import metadata
import datetime

source = "https://stringdb-static.org/download/protein.actions.v11.0/9606.protein.actions.v11.0.txt.gz"
mapping = "https://string-db.org/mapping_files/uniprot/human.uniprot_2_string.2018.tsv.gz"

def evaLink(term1, term2, predicate, link_type="ListLink",stv="", ppi=True):
    if not (str(term1) == "nan" or str(term2) == 'nan'):
        if ppi:
            return("(EvaluationLink" + stv + "\n" +
                "\t (PredicateNode \""+ predicate + "\")\n" +
                "\t (" + link_type + " \n" +
                "\t\t (MoleculeNode" + " \"Uniprot:" + term1 + "\")\n" +
                "\t\t (MoleculeNode" + " \"Uniprot:" + term2 + "\")))\n" )
        else:
            return("(EvaluationLink" + stv + "\n" +
            "\t (PredicateNode \""+ predicate + "\")\n" +
            "\t (" + link_type + " \n" +
            "\t\t (GeneNode" + " \"" + term1.upper() + "\")\n" +
            "\t\t (GeneNode" + " \"" + term2.upper() + "\")))\n" )
    else:
        return ""
def import_string():
    print("started at " + str(datetime.datetime.now()))
    if not os.path.exists('raw_data/9606.protein.actions.v11.0.txt.gz'):
        wget.download(source,"raw_data/")
    if not os.path.exists('raw_data/human.uniprot_2_string.2018.tsv.gz'):
        wget.download(mapping,"raw_data/")
    
    df_data = pd.read_csv("raw_data/9606.protein.actions.v11.0.txt.gz", dtype=str, sep="\t")
    df_data_symmetric = df_data[df_data['is_directional'] == "f"]
    df_data_asymmetric = df_data[df_data['is_directional'] == "t"]
    df_mapping = pd.read_csv("raw_data/human.uniprot_2_string.2018.tsv.gz", dtype=str, sep="\t", names=["code", "uniprot", "ensembl","num1","num2"])
   
    # create a mapping dictionary
    mapping_dict = {} 
    for e in df_mapping["ensembl"]:
        if not e in mapping_dict.keys():
            mapping_dict[e] = df_mapping[df_mapping["ensembl"] == e]["uniprot"].values[0]
    print("Done with the Dict, importing into atomese")
    print(len(df_data))
    notmapped = []

    """
        If the directionality of the interaction is true and a is acting, use ListLink and keep the order. Otherwise use SetLink
        * is_directional - describes if the diractionality of the particular interaction is known.
        * a_is_acting - the directionality of the action if applicable ('t' gives that item_id_a is acting upon item_id_b)
        Example:
        item_id_a   item_id_b   mode    is_directional  a_is_acting
        ENSP00000000233	ENSP00000216366 reaction    f   f   
        <=> EvaluationLink 
                PredicateNode "reaction"
                SetLink ENSP00000000233 ENSP00000216366

        ENSP00000000233	ENSP00000216366 reaction    t   f
        <=> EvaluationLink 
                PredicateNode "reaction"
                ListLink ENSP00000216366 ENSP00000000233
        ENSP00000000233	ENSP00000216366	reaction    t   t
        <=> EvaluationLink 
                PredicateNode "reaction"
                ListLink ENSP00000000233 ENSP00000216366
    
        Keep symmetric relations and ignore if the same relation happens to be asymmetric
    """
    symmetric = {}
    if not os.path.exists(os.path.join(os.getcwd(), 'string_dataset')):
        os.makedirs('string_dataset')
    with open("string_dataset/string_ppi_{}.scm".format(str(datetime.date.today())), "w") as f, open('string_dataset/string_ggi_{}.scm'.format(str(datetime.date.today())), 'w') as g:
        for i in range(len(df_data_symmetric)):
            try:
                prot1 = df_data_symmetric.iloc[i]['item_id_a']
                prot2 = df_data_symmetric.iloc[i]['item_id_b']
                mode = df_data_symmetric.iloc[i]['mode']
                score = int(df_data_symmetric.iloc[i]['score'])               

                if prot1 in mapping_dict.keys() and prot2 in mapping_dict.keys():
                    prot1 = mapping_dict[prot1]
                    prot2 = mapping_dict[prot2]
                else:
                    if not prot1 in mapping_dict.keys():
                        notmapped.append(prot1)
                    else:
                        notmapped.append(prot2)
                    continue
                
                protein1 = prot1.split("|")[0]
                gene1 = prot1.split("|")[1].split("_")[0] 
                protein2 = prot2.split("|")[0]
                gene2 = prot2.split("|")[1].split("_")[0]

                f.write(evaLink(protein1, protein2, mode, stv="(stv {} {})".format(1.0, score/1000),link_type="SetLink"))
                g.write(evaLink(gene1, gene2, mode,stv="(stv {} {})".format(1.0, score/1000), link_type="SetLink", ppi=False))  
                symmetric[gene1 + gene2] = mode

            except Exception as e:
                print(e)
        for i in range(len(df_data_asymmetric)):
            try:
                prot1 = df_data_asymmetric.iloc[i]['item_id_a']
                prot2 = df_data_asymmetric.iloc[i]['item_id_b']
                mode = df_data_asymmetric.iloc[i]['mode']
                a_is_acting = df_data_asymmetric.iloc[i]['a_is_acting'] 
                score = int(df_data_asymmetric.iloc[i]['score'])               

                if prot1 in mapping_dict.keys() and prot2 in mapping_dict.keys():
                    prot1 = mapping_dict[prot1]
                    prot2 = mapping_dict[prot2]
                else:
                    if not prot1 in mapping_dict.keys():
                        notmapped.append(prot1)
                    else:
                        notmapped.append(prot2)
                    continue
                
                protein1 = prot1.split("|")[0]
                gene1 = prot1.split("|")[1].split("_")[0] 
                protein2 = prot2.split("|")[0]
                gene2 = prot2.split("|")[1].split("_")[0]

                if not (gene1+gene2 in symmetric.keys() and symmetric[gene1+gene2] == mode):
                    if a_is_acting is "t": 
                        f.write(evaLink(protein1, protein2, mode, stv="(stv {} {})".format(1.0, score/1000)))
                        g.write(evaLink(gene1, gene2, mode, stv="(stv {} {})".format(1.0, score/1000), ppi=False))
                    else:
                        f.write(evaLink(protein2, protein1, mode, stv="(stv {} {})".format(1.0, score/1000)))
                        g.write(evaLink(gene2, gene1, mode, ppi=False, stv="(stv {} {})".format(1.0, score/1000)))

            except Exception as e:
                print(e)
        
        print("Done " + str(datetime.datetime.now()))
        with open("string_dataset/notmapped_ensembles.txt", "w") as n:
            n.write("\n".join(set(notmapped)))

if __name__ == "__main__":
    import_string()