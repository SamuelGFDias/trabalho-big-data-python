from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

class SVMService:
    def __init__(self, pipeline: bool = False):
        self.pipeline = pipeline
        self.model = None
        self.X_test = None
        self.y_test = None

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=1
        )
        if self.pipeline:
            clf = Pipeline([
                ('scaler', StandardScaler()),
                ('svc', SVC(gamma='auto'))
            ])
        else:
            clf = SVC(gamma='auto')

        clf.fit(X_train, y_train)
        self.model = clf
        self.X_test = X_test
        self.y_test = y_test

    def predict(self):
        y_pred = self.model.predict(self.X_test)
        return accuracy_score(self.y_test, y_pred)