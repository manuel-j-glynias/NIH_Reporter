import sys
import os
import time
import datetime

from util import replace_characters

os.environ['NCBI_API_KEY'] = 'cde5c1a63fa16711994bfe74b858747cbb08'
from metapub import PubMedFetcher
import re
import unicodedata as ud

cache = '/Users/mglynias/Documents/GitHub/OmniSeqKnowledgebase_populate/cache'


def rmdiacritics(char):
    '''
    Return the base character of char, by "removing" any
    diacritics like accents or curls and strokes and the like.  ð
    '''
    if char == "æ":
        return 'ae'
    elif char == 'ß':
        return 's'
    elif char == 'ð':
        return 'd'
    else:
        desc = ud.name(char)
        cutoff = desc.find(' WITH ')
        if cutoff != -1:
            desc = desc[:cutoff]
            try:
                char = ud.lookup(desc)
            except KeyError:
                pass  # removing "WITH ..." produced an invalid name
        return char

def remove_accents(input_str):
    nfkd_form = ud.normalize('NFKD', input_str)
    return u"".join([rmdiacritics(c) for c in input_str])



def PMID_extractor(text:str)->list:
    pattern = r'PMID:\s+\d{8}'
    matches = re.findall(pattern,text)
    pmids = []
    for match in matches:
        if match not in pmids:
            pmids.append(match)
    return pmids

def PubMed_extractor(text:str)->list:
    pattern = r'PubMed:\d{8}'
    matches = re.findall(pattern,text)
    pmids = []
    for match in matches:
        match = match[7:]
        if match not in pmids:
            pmids.append(match)
    return pmids

def get_reference_from_pmid_by_metapub(pmid:str)->dict:
    fetch = PubMedFetcher(cachedir=cache)
    reference = None
    try:
        time.sleep(0.34)
        article = fetch.article_by_pmid(pmid)
        reference = {'journal':article.journal,
                     'authors': article.authors,
                     'issue':article.issue,
                     'first_page':article.first_page,
                     'last_page': article.last_page,
                     'volume':article.volume,
                     'year': str(article.year),
                     'abstract': replace_characters(article.abstract),
                     'title': replace_characters(article.title),
                     'doi': article.doi,
                     'pmid': article.pmid
                     }
    except:
        print('*** Bad PMID:',pmid)

    return reference

def get_authors_names(author):
    l = author.split()
    first = '-'
    if (len(author) - len(l[0])) > 5:
    #     must be name of organization
        surname = replace_characters(author)
    else:
        surname = replace_characters(l[0])
        if len(l)>1:
            first = replace_characters(l[1])
    return first, surname

def ref_name_from_authors_pmid_and_year(authors, pmid, year):
    s = ''
    if len(authors)>0:
        first, surname = get_authors_names(authors[0])
        if len(authors) == 1:
            s += surname + ' ' + year
        elif len(authors) == 2:
            first2, surname2 = get_authors_names(authors[1])
            s += surname + ' & '+ surname2 + ' ' + year
        else:
            s += surname + ' et al. ' + year
    else:
        s += 'no_authors ' + year
    s += ' (PMID:' + pmid + ')'
    return s


def create_reference_mutation(ref_id, ref):
    ref_name = ref_name_from_authors_pmid_and_year(ref['authors'], ref['pmid'], ref['year'])
    s = f'''{ref_id}: createLiteratureReference(id: \\"{ref_id}\\", abstract: \\"{ref['abstract']}\\", shortReference: \\"{ref_name}\\", title: \\"{ref['title']}\\", volume: \\"{ref['volume']}\\", firstPage: \\"{ref['first_page']}\\", lastPage: \\"{ref['last_page']}\\", publicationYear: \\"{ref['year']}\\", DOI: \\"{ref['doi']}\\", PMID: \\"{ref['pmid']}\\"),'''
    return s


def create_author_mutation(id,surname,first):
    s = f'''{id}: createAuthor(firstInitial: \\"{first}\\" , id: \\"{id}\\",surname: \\"{surname}\\"),'''
    return s


def create_journal_mutation(journal, journal_id):
    s = f'''{journal_id}: createJournal(id: \\"{journal_id}\\",name: \\"{journal}\\"),'''
    return s


def create_AddLiteratureReferenceJournal_mutation(ref_id, journal_id):
    id = ref_id + '_' + journal_id
    s = f'{id}: addLiteratureReferenceJournal(id:\\"{ref_id}\\", journal:\\"{journal_id}\\"),'
    return s

def create_AddLiteratureReferenceAuthors_mutation(ref_id, authors):
    id = 'author_' +ref_id
    author_string = '['
    for a in authors:
        if len(author_string)>1:
            author_string += ","
        author_string += '\\"' + a + '\\"'
    author_string += ']'
    s = f'{id}: addLiteratureReferenceAuthors(id:\\"{ref_id}\\", authors:{author_string}),'

    return s

def fix_author_id(id:str)->str:
    id = id.lower()
    id = remove_accents(id)
    id = id.replace(" ","_");
    id = id.replace(" ", "_")
    id = id.replace(":", "")
    id = id.replace(",", "")
    id = id.replace("(", "")
    id = id.replace(")", "")
    id = id.replace("<sup>®<_sup>","")
    id = id.replace("<", "")
    id = id.replace(">", "")
    id = id.replace("®", "_")
    id = id.replace("-", "_")
    id = id.replace("'", "_")
    id = id.replace("ʼ", "_")
    id = id.replace("ʼ", "_")
    id = id.replace(".", "_")
    id = id.replace("/", "_")
    id = id.replace("-", "_")
    id = id.replace(". .",".")

    return id


def write_references(pubmed:str,reference_dict:dict,journal_dict:dict,author_dict:dict)->str:
    reference = get_reference_from_pmid_by_metapub(pubmed)
    s: str = ''
    ref_id: str = ''
    if reference != None:
        s: str = ''
        if pubmed not in reference_dict:
            ref_id = 'ref_' + pubmed
            s += create_reference_mutation(ref_id, reference)
            reference_dict[pubmed] = ref_id
            journal = reference['journal']
            if journal not in journal_dict:
                journal_id = 'journal_' + fix_author_id(journal)
                s += create_journal_mutation(journal, journal_id)
                journal_dict[journal] = journal_id
            else:
                journal_id = journal_dict[journal]
            s += create_AddLiteratureReferenceJournal_mutation(ref_id, journal_id)
            authors = []
            for author in reference['authors']:
                first, surname = get_authors_names(author)
                key = fix_author_id(surname + '_' + first)
                if key not in author_dict:
                    author_id = 'author_' + surname + '_' + first
                    author_id = fix_author_id(author_id)
                    s += create_author_mutation(author_id, surname, first)
                    author_dict[key] = author_id
                else:
                    author_id = author_dict[key]
                authors.append(author_id)
            s += create_AddLiteratureReferenceAuthors_mutation(ref_id, authors)
        else:
            ref_id = reference_dict[pubmed]
    return s,ref_id


if __name__ == '__main__':
    pubmed: str= '32869375'
    reference_dict: dict = {}
    journal_dict: dict = {}
    author_dict: dict= {}
    s,ref_id = write_references(pubmed,reference_dict,journal_dict,author_dict)
    print(s)
    print(ref_id)

