from collections import Counter
import operator
import matplotlib.pyplot as plt
import numpy as np

def run_cats(df):
    all_cats = output_all_cats(df)
    good_cats = bad_cats(all_cats)
    cnt_cats = count_cats(good_cats, debug=False)
    out_cats, _ = min_cats(cnt_cats, N=2)
    return out_cats



def output_all_cats(df):
    """ Returns list of all categories including duplicates, except those that
        contain author's name or 'Google Art Project'  """
    all_cats = []
    for i, row in df.iterrows():
        cat = row['categories']
        artist = row['artist_name']
        if cat is not None:
            cat_list = cat.split('||')
            for c in cat_list:
                if "Google Art Project" in c:
                    continue
                if artist in c:
                    continue
                # if c in all_cats:
                #     continue
                # Otherwise add to list
                all_cats.append(c)
    return all_cats

def count_cats(cat_list, debug=False):
    """ Returns a list of tuples with cat name and count (# of duplicates) """
    counts = Counter(cat_list)
    sorted_counts = sorted(counts.items(), key=operator.itemgetter(1))
    if debug:
        for i in sorted_counts[-50:]:
            print(str(i[1]) + ' -- ' + i[0])
    return sorted_counts

def cat_histogram(sorted_counts):
    cnt = []
    for i in sorted_counts:
        cnt.append(i[1])
    plt.hist(cnt,np.arange(0,110,5), log=True)
    plt.show()
    return None

def min_cats(sorted_counts, N=2):
    """Given list of tuples of cats, return a list of cats that appear more
       frequently than N times (2 by default). Also return a list of tuples"""
    out_list = []
    out_tup_list = []
    for i in sorted_counts:
        if i[1] > N:
            out_list.append(i[0])
            out_tup_list.append((i[0], i[1]))
    return out_list, out_tup_list


def bad_cats(all_cats):
    """ Removes any cateogry from list that has one of the following terms """
    bad = ['Artworks with known accession number',
           'Artworks with accession number from Wikidata',
           'Artworks without Wikidata item',
           'Artworks with Wikidata item',
           'Unsupported object',
           'Template Unknown (author)',
           'MS. LUDWIG XV 13 (Getty museum) - The Flower of Battle',
           'Drawings of animals by George Stubbs',
           'Italy in art by John Robert Cozens',
           'The Domain, Sydney',
           'The Channel Sketchbook by Joseph Mallord William Turner',
           'Large images',
           'Nuenen',
           'Collections of the Yale Center for British Art',
           'Featured pictures on Wikipedia, English',
           'Egypt by Edward Lear',
           'Chelsea',
           'Jerusalem The Emanation of the Giant Albion - copy E',
           'Songs of Innocence and Experience - Copy L',
           'Works by Gauguin by Wildenstein Index Number',
           'Sala del Mappamondo (Palazzo Vecchio)',
           'Artwork template with implicit institution',
           'Paintings in Tate Britain',
           'Pages using ISBN magic links',
           'Works by Van Gogh by Faille number',
           'All media needing categories',
           'Works by Van Gogh by JH number',
           'Doha Museum of Islamic Art',
           "MS LUDWIG IX 13 (Getty museum) - Gualenghi-d'Este Hours",
           'Getty Museum',
           'Images from The Israel Museum, Jerusalem',
           'Songs of Innocence - Copy G 1789',
           'Songs of Innocence and Experience - Copy F',
           'Files uploaded by ',
           'Paintings uploaded by ',
           'Paintings with years of production (artist)',
           'Pages using duplicate arguments in template calls',
           'Whistler collection at the Freer Gallery of Art',
           ' in the ',
           'Collections of ']
    # Initialize the good cats
    good = []
    blen = len(bad)
    # Loop over input category list
    for c in all_cats:
        count = 0
        # Loop over "bad" categories
        for b in bad:
            # Count the number of times the item doesn't appear in the bad cat
            if b not in c:
                count += 1
        # If it doesn't appear, add it to the good list
        if count == blen:
            good.append(c)
    return good
