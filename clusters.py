import numpy as np
import sklearn.cluster

def do_cluster(df, df_feat, load_file=False):
    """Does k-means clustering with 18 clusters on features
    IN~~~
       df -- the dataframe w/o features
       df_feat -- the dataframe w/ features alone
       load_file -- boolean about whether to load the cluster labels from file
    OUT~~~
       df -- dataframe w/o features, but with cluster labels   """
    if load_file:
        out18labels = np.load('./files/clusters18.npy')
    else:
        out18 = sklearn.cluster.KMeans(n_clusters=18).fit(df_feat)
        out18labels = out18.labels_
    df['cluster'] = out18labels
    return df

def get_cluster_unique(df, df_feat):
    cattype = []
    for i in range(18):
        num = df_feat[(df['cluster']==i)].sum()
        denom = (df['cluster']==i).sum()
        out = (num / denom).sort_values(na_position='last')[::-1][:20]
        cattype.append(out[out > 0.2].index.tolist())
        cattype[-1] = [c[7:] for c in cattype[-1]]
    return cattype
