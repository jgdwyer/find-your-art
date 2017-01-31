from collections import Counter
import operator
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re

def run_cats(df):
    # Get most categories including duplicates (but not GAP or artist)
    all_cats = output_all_cats(df)
    # Exclude very common, unuseful categories
    good_cats = bad_cats(all_cats)
    # Exclude categories with explicit years -- these are too narrow
    good_cats = year_cats(good_cats)
    # Get count frequency
    cnt_cats = count_cats(good_cats, debug=False)
    # Limit to categories that have at least two entries
    out_cats, _ = min_cats(cnt_cats, N=1)
    return out_cats

def one_hot_encoding(df):
    """Perform one-hot encoding to convert all categories to 1/0 and add many
    new rows to the original data frame"""
    df2 = df['categories_cleaned'].str.get_dummies()
    df = pd.concat([df, df2], axis=1)
    return df

def remove_some_cats_from_df(df, make_hist=False, debug=False):
    """Adds a new column to the dataframe (categories_cleaned) that does not
       include extranenous categories"""
    # Add a new column initialized with nans to the data frame
    df['categories_cleaned'] = None #pd.Series(None, index=df.index)
    # This returns a list of good cats
    new_cat_list = run_cats(df)
    # Iterate over each row of dataframe
    rowlen=[]
    for i, row in df.iterrows():
        # Show progress
        if i%1000==1:
            print(i)
        # Get a list of the original categories for this entry
        if row['categories'] is None:
            continue
        orig_cats = row['categories'].split("||")
        less_cats = []
        # Check to see if they are in "out_cats"
        for orig_cat in orig_cats:
            if orig_cat in new_cat_list:
                less_cats.append('catbin:' + orig_cat)
        # Save as new row entry and join strings in list again on delimter
        df.set_value(i, 'categories_cleaned', '||'.join(less_cats))
        # Count number of categories for each entry
        rowlen.append(len(less_cats))
        if debug and i<300:
            print(orig_cats)
            print(less_cats)
            print('--------------------------')

    if make_hist:
        plt.hist(rowlen, bins=np.arange(0,15,1),log=True)
        plt.show()
    return df


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

def min_cats(sorted_counts, N=1):
    """Given list of tuples of cats, return a list of cats that appear more
       frequently than N times (1 by default). Also return a list of tuples"""
    out_list = []
    out_tup_list = []
    for i in sorted_counts:
        if i[1] > N:
            out_list.append(i[0])
            out_tup_list.append((i[0], i[1]))
    return out_list, out_tup_list

def year_cats(in_cats):
    out_cats = []
    for c in in_cats:
        if re.search(r'[12]\d{3}', c) is None:
            out_cats.append(c)
    return out_cats

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
           'Files not protected by international copyright agreements',
           '(page does not exist)'] #,
        #    'Museum',
        #    'Gallery',
        #    ' in the ',
        #    'Collections of ']
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
