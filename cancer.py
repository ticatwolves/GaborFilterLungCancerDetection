from sklearn import svm
import csv
import pandas as pd
import cv2
import numpy as np
import pylab as pl
import glob


class Cancer(object):

    def __init__(self):
        self.filters = self.build_filters()

    def build_filters(self):
        filters = []
        ksize = 9
        for theta in np.arange(0, np.pi, np.pi / 8):
            for nu in np.arange(0, 6*np.pi/4 , np.pi / 4):
                kern = cv2.getGaborKernel((ksize, ksize), 1.0, theta, nu, 0.5, 0, ktype=cv2.CV_32F)
                kern /= 1.5*kern.sum()
                filters.append(kern)
        return filters

    def process(self, img, filters):
        accum = np.zeros_like(img)
        for kern in filters:
            fimg = cv2.filter2D(img, cv2.CV_8UC3, kern)
            np.maximum(accum, fimg, accum)
        return accum
    def make_features(self, img):
        f = np.asarray(self.filters)
        imgg = cv2.imread(img)#<- address of images
        feat = []
        for j in range(40):
            res = self.process(imgg, f[j])
            temp = 0
            for p in range(128):
                for q in range(128):
                    temp = temp + res[p][q]*res[p][q]
            feat.extend(temp)
        for j in range(40):
            res = self.process(imgg, f[j])
            temp = 0
            for p in range(128):
                for q in range(128):
                    temp = temp + abs(res[p][q])
            feat.extend(temp)
        return feat

    def predict(self, image, gender, age):
        gender = 0 if gender == 'M' else 1
        try:
            features_file = open('features_matrix.csv')
            labels_file = open('no_labels.csv')
            labels_file_two = open('labels.csv')
        except:
            return {'error': 'Data not made'}
        features = list(csv.reader(features_file))
        labels = list(csv.reader(labels_file))
        labels_two = list(csv.reader(labels_file_two))
        clf = svm.SVC(gamma = 0.0001)
        clf.fit(features, labels)
        clf2 = svm.SVC(gamma = 0.0001)
        clf2.fit(features, labels_two)
        test_features = self.make_features(image)
        cc = [int(age), int(gender)]
        cc.extend(test_features)
        cancer_or_not = clf.predict([cc])
        cancer_label = clf2.predict([cc])
        labels_file.close()
        features_file.close()
        labels_file_two.close()
        cancer = ['No Findings', 'Cancer']
        cancer_type = []
        return {
            'cancer': cancer[cancer_or_not],
            'cancer_type':  cancer_type[cancer_label]
        }

    def make_csv(self):
        images = glob.glob("images/*.png")
        sample_csv = pd.read_csv('sample_labels.csv')
        response = []
        labels = []
        cancer_type = []
        for index, image in enumerate(images):
            reatures = self.make_features(image)
            data = []
            for i in range(0, len(sample_csv)):
                if sample_csv.iloc[i]['Image Index'] == image.split('/')[-1]:
                    try:
                        try:
                            label = 0 if sample_csv.iloc[i]['Finding Labels'] == 'No Finding' else 1
                            gender = 0 if sample_csv.iloc[i]['Patient Gender'] == 'M' else 1
                            patient_age = int(str(sample_csv.iloc[i]['Patient Age']).split('Y')[0])
                            data = [patient_age, gender]
                            for de in feat:
                                data.append(de)
                            response.append(data)
                            labels.append(label)
                            cancer_type.append(sample_csv.iloc[i]['Finding Labels'])
                        except:
                            label = 0 if sample_csv.iloc[i]['Finding Labels'] == 'No Finding' else 1
                            gender = 0 if sample_csv.iloc[i]['Patient Gender'] == 'M' else 1
                            patient_age = int(str(sample_csv.iloc[i]['Patient Age']).split('M')[0])
                            data = [patient_age, gender]
                            for de in feat:
                                data.append(de)
                            response.append(data)
                            labels.append(label)
                            cancer_type.append(sample_csv.iloc[i]['Finding Labels'])
                    except:
                        pass
            print(index)
        with open('features_matrix.csv', 'w+') as fe:
            wr = csv.writer(fe)
            wr.writerrows(response)
        with open('no_labels.csv', 'w+') as fe:
            wr = csv.writer(fe)
            wr.writerrows(labels)
        with open('labels.csv', 'w+') as fe:
            wr = csv.writer(fe)
            wr.writerrows(cancer_type)

if __name__ == "__main__":
    can = Cancer()
    can.make_csv()