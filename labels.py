import io
import os
import os.path
# Imports the Google Cloud client library
from google.cloud import vision
import cats

def add_labels_to_df(df):
    # Add new columns to df
    df = df.assign(label_names = None)
    df = df.assign(label_scores = None)
    # Loop over rows
    for i, row in df.iterrows():
        if i%20==1:
            print(i)
            df.to_pickle('./dfs/tmp'+str(i)+'.pickle')
        row_labels = None
        row_scores = None
        if row['filename_nospaces'] is None:
            continue
        ptf = './im/' + row['filename_nospaces']
        #Ensure that file exists locally
        if os.path.isfile(ptf):
            row_labels, row_scores = get_labels(ptf, local=True, debug=False)
            row_labels = "||".join(row_labels)
            row_scores = "||".join(map(str, row_scores))
            #Update dataframe
            df.set_value(i, 'label_names', row_labels)
            df.set_value(i, 'label_scores', row_scores)
    return df

def get_labels(ptf, local=True, debug=False):
    # Instantiates a client
    vision_client = vision.Client()

    # The name of the image file to annotate
    #file_name = os.path.join(
    #    os.path.dirname(__file__),
    #    'resources/wakeupcat.jpg')
    if local:
        # Loads the image into memory
        with io.open(ptf, 'rb') as image_file:
           content = image_file.read()
           image = vision_client.image(
               content=content)
    else:
        image = vision_client.image(source_uri='gs://jgd-insight-bucket1/' + ptf)

    row_labels = []
    row_scores = []
    # Performs label detection on the image file
    labels = image.detect_labels()
    if debug:
        print('Labels for ' + ptf)
    for label in labels:
        row_labels.append(label.description)
        row_scores.append(label.score)
    return row_labels, row_scores

def output_all_labels(df):
    all_lab=[]
    for i, row in df.iterrows():
        lab=row['label_names']
        if lab is not None:
            lab_list = lab.split('||')
            for l in lab_list:
                all_lab.append(l)
    return all_lab

def run_labels(df):
    all_labs = output_all_labels(df)
    cnt_labels = cats.count_cats(all_labs, debug=False)
    out_labels, out_tup_list = cats.min_cats(cnt_labels, N=1)
    # out_labels is the unique labels occuring more than once
    return out_labels, out_tup_list
