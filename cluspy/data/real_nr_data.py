import numpy as np
import os
from cluspy.data.real_world_data import _get_download_dir, _download_file
import tarfile
import re
from sklearn.feature_extraction.text import TfidfTransformer, CountVectorizer
from sklearn.feature_selection import VarianceThreshold
from nltk.stem import SnowballStemmer
from PIL import Image


def _laod_nr_data(file_name, n_labels):
    """
    Helper function to load a non-redundant data set from ClusPys internal data sets directory.
    The first n_labels columns will be specified as labels.

    Parameters
    ----------
    file_name: Name of the data set
    n_labels: Number of label sets

    Returns
    -------
    data: the data numpy array
    labels: the labels numpy array
    """
    path = os.path.dirname(__file__) + "/datasets/" + file_name
    dataset = np.genfromtxt(path, delimiter=",")
    data = dataset[:, n_labels:]
    labels = dataset[:, :n_labels]
    return data, labels


def load_aloi_small():
    """
    Load a subset of the Amsterdam Library of Object Image (ALOI) consisting of 288 images of the objects red ball,
    red cylinder, green ball and green cylinder. The two label sets are cylinder/ball and red/green.
    N=288, d=611, k=[2,2].

    Returns
    -------
    data: the data numpy array (288 x 611)
    labels: the labels numpy array (288 x 2)

    References
    -------
    https://aloi.science.uva.nl/

    and

    Ye, Wei, et al. "Generalized independent subspace clustering." 2016 IEEE 16th International Conference on Data
    Mining (ICDM). IEEE, 2016.
    """
    return _laod_nr_data("aloi_small.data", 2)


def load_fruit():
    """
    Load the fruits data set. It consists of 105 preprocessed images of apples, bananas and grapes in red, green and yellow.
    N=105, d=6, k=[3,3].

    Returns
    -------
    data: the data numpy array (105 x 6)
    labels: the labels numpy array (105 x 2)

    References
    -------
    Hu, Juhua, et al. "Finding multiple stable clusterings." Knowledge and Information Systems 51.3 (2017): 991-1021.
    """
    return _laod_nr_data("fruit.data", 2)


def load_nrletters():
    """
    Load the NRLetters data set. It consists of 10000 9x7 images of the letters A, B, C, X, Y and Z in pink, cyan and
    yellow. Additionally, each image highlights one corner in color.
    N=10000, d=189, k=[6,3,4].

    Returns
    -------
    data: the data numpy array (10000 x 189)
    labels: the labels numpy array (10000 x 3)

    References
    -------
    Leiber, Collin, et al. "Automatic Parameter Selection for Non-Redundant Clustering." Proceedings of the 2022 SIAM
    International Conference on Data Mining (SDM). Society for Industrial and Applied Mathematics, 2022.
    """
    return _laod_nr_data("nrLetters.data", 3)


def load_stickfigures():
    """
    Load the Dancing Stick Figures data set. It consists of 900 20x20 grayscale images of stick figures in different poses.
    The poses can be divided into three upp-body and three lower-body motions.
    N=900, d=400, k=[3,3].

    Returns
    -------
    data: the data numpy array (900 x 400)
    labels: the labels numpy array (900 x 2)

    References
    -------
    Günnemann, Stephan, et al. "Smvc: semi-supervised multi-view clustering in subspace projections." Proceedings of
    the 20th ACM SIGKDD international conference on Knowledge discovery and data mining. 2014.
    """
    return _laod_nr_data("stickfigures.data", 2)


"""
UCI
"""


def load_cmu_faces(downloads_path=None):
    """
    Load the CMU Face Images data set. It consists of 640 30x32 grayscale images showing 20 persons in different poses
    (up, straight, left, right) und with different expressions (neutral, happy, sad, angry). Additionally, the persons
    can wear sunglasses or not.
    16 images show glitches which is why the final data set only contains 624 images.
    N=624, d=400, k=[20,4,4,2].

    Parameters
    -------
    downloads_path: path to the directory where the data is stored (default: None -> [USER]/Downloads/cluspy_datafiles)

    Returns
    -------
    data: the data numpy array (624 x 400)
    labels: the labels numpy array (624 x 4)

    References
    -------
    http://archive.ics.uci.edu/ml/datasets/cmu+face+images
    """
    directory = _get_download_dir(downloads_path) + "/cmufaces/"
    filename = directory + "faces_4.tar.gz"
    if not os.path.isfile(filename):
        if not os.path.isdir(directory):
            os.mkdir(directory)
        _download_file("http://archive.ics.uci.edu/ml/machine-learning-databases/faces-mld/faces_4.tar.gz",
                       filename)
        # Unpack zipfile
        with tarfile.open(filename, "r:gz") as tar:
            tar.extractall(directory)
    names = np.array(
        ["an2i", "at33", "boland", "bpm", "ch4f", "cheyer", "choon", "danieln", "glickman", "karyadi", "kawamura",
         "kk49", "megak", "mitchell", "night", "phoebe", "saavik", "steffi", "sz24", "tammo"])
    positions = np.array(["straight", "left", "right", "up"])
    expressions = np.array(["neutral", "happy", "sad", "angry"])
    eyes = np.array(["open", "sunglasses"])
    data_list = []
    label_list = []
    for name in names:
        path_images = directory + "/faces_4/" + name
        for image in os.listdir(path_images):
            if not image.endswith("_4.pgm"):
                continue
            # get image data
            image_data = Image.open(path_images + "/" + image)
            image_data_vector = np.array(image_data).reshape(image_data.size[0] * image_data.size[1])
            # Get labels
            name_parts = image.split("_")
            user_id = np.argwhere(names == name_parts[0])[0][0]
            position = np.argwhere(positions == name_parts[1])[0][0]
            expression = np.argwhere(expressions == name_parts[2])[0][0]
            eye = np.argwhere(eyes == name_parts[3])[0][0]
            label_data = np.array([user_id, position, expression, eye])
            # Save data and labels
            data_list.append(image_data_vector)
            label_list.append(label_data)
    labels = np.array(label_list)
    data = np.array(data_list)
    return data, labels


"""
Load WebKB
"""


def load_webkb(use_universities=["cornell", "texas", "washington", "wisconsin"],
               use_categories=["course", "faculty", "project", "student"], remove_headers=True,
               min_doc_frequency=0.01, min_variance=0.25, downloads_path=None):
    """
    Load the WebKB data set. It consists of 1041 Html documents from different universities (default: "cornell", "texas",
    "washington" and "wisconsin"). These web pages have a specified category (default: "course", "faculty", "project",
    "student"). For more information see the references website.
    The data is preprocessed by using stemming and removing stop words. Furthermore, words with a document frequency
    smaller than min_doc_frequency or with a variance smaller than min_variance will be removed.
    N=1041, d=323, k=[4,4] using the default settings.

    Parameters
    ----------
    use_universities: specify the universities (default: ["cornell", "texas", "washington", "wisconsin"]
    use_categories: specify the categories (default: ["course", "faculty", "project", "student"]
    remove_headers: should the headers of the Html files be removed? (default: True)
    min_doc_frequency: minimum document frequency of the words (default: 0.01)
    min_variance: minimum variance of the words (default: 0.25)
    downloads_path: path to the directory where the data is stored (default: None -> [USER]/Downloads/cluspy_datafiles)

    Returns
    -------
    data: the data numpy array (1041 x 323) using the default settings
    labels: the labels numpy array (1041 x 2) using the default settings

    References
    -------
    http://www.cs.cmu.edu/~webkb/
    """
    directory = _get_download_dir(downloads_path) + "/WebKB/"
    filename = directory + "webkb-data.gtar.gz"
    if not os.path.isfile(filename):
        if not os.path.isdir(directory):
            os.mkdir(directory)
        _download_file("http://www.cs.cmu.edu/afs/cs.cmu.edu/project/theo-20/www/data/webkb-data.gtar.gz",
                       filename)
        # Unpack zipfile
        with tarfile.open(filename, "r:gz") as tar:
            for obj in tar.getmembers():
                if obj.isdir():
                    # Create Directory
                    tar.extract(obj, directory)
                else:
                    # Can not handle filenames with special characters. Therefore, rename files
                    new_name = obj.name.replace("~", "_").replace(".", "_").replace("^", "_").replace(":", "_").replace(
                        "\r", "")
                    # Get file content
                    f = tar.extractfile(obj)
                    lines = f.readlines()
                    # Write file
                    with open(directory + new_name, "wb") as output:
                        for line in lines:
                            output.write(line)
    texts = []
    labels = np.empty((0, 2), dtype=np.int)
    hmtl_tags = re.compile(r'<[^>]+>')
    head_tags = re.compile(r'MIME-Version:[:,./\-\w\s]+<html>')
    number_tags = re.compile(r'\d*')
    # Read files
    for i, category in enumerate(use_categories):
        for j, univerity in enumerate(use_universities):
            inner_directory = "{0}webkb/{1}/{2}/".format(directory, category, univerity)
            files = os.listdir(inner_directory)
            for file in files:
                with open(inner_directory + file, "r", encoding='latin-1') as f:
                    lines = f.read()
                    if remove_headers:
                        # Remove header
                        lines = head_tags.sub('', lines)
                    # Remove HTML tags
                    lines = hmtl_tags.sub('', lines)
                    lines = number_tags.sub('', lines)
                    texts.append(lines)
                    labels = np.r_[labels, [[i, j]]]
    # Execute TF-IDF, remove stop-words and use the snowball stemmer
    vectorizer = _StemmedCountVectorizer(dtype=np.float64, stop_words="english", min_df=min_doc_frequency)
    data_sparse = vectorizer.fit_transform(texts)
    selector = VarianceThreshold(min_variance)
    data_sparse = selector.fit_transform(data_sparse)
    tfidf = TfidfTransformer(sublinear_tf=True)
    data_sparse = tfidf.fit_transform(data_sparse)
    data = np.asarray(data_sparse.todense())
    return data, labels


class _StemmedCountVectorizer(CountVectorizer):
    """
    Helper class for load_webkb(). Combines the CountVectorizer with the SnowballStemmer.
    See: https://stackoverflow.com/questions/36182502/add-stemming-support-to-countvectorizer-sklearn
    """

    def build_analyzer(self):
        stemmer = SnowballStemmer('english')
        analyzer = super(_StemmedCountVectorizer, self).build_analyzer()
        return lambda doc: (stemmer.stem(word) for word in analyzer(doc))
