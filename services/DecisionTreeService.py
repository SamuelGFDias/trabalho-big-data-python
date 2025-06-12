from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

class DecisionTreeService:
    def __init__(self):
        self.model = None
        self.X_test = None
        self.y_test = None

    def train(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.3, random_state=1
        )
        clf = tree.DecisionTreeClassifier()
        clf.fit(X_train, y_train)

        self.model = clf
        self.X_test = X_test
        self.y_test = y_test

    def predict(self):
        y_pred = self.model.predict(self.X_test)
        return accuracy_score(self.y_test, y_pred)