import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def prepare_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    X = df.drop(["uhi_medio", "ciudad", "uhi_dia", "uhi_noche"], axis=1)
    y = df["uhi_medio"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, train_size=0.75, random_state=33
    )

    return (X_train, X_test, y_train, y_test)


def train_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.DataFrame,
    y_test: pd.DataFrame,
) -> tuple[dict, pd.Series]:
    models = {
        "Lineal": LinearRegression(),
        "Ridge": Ridge(alpha=1),
        "Lasso": Lasso(alpha=1),
    }

    r2 = {}

    for name, model in models.items():
        pipe = Pipeline([("preprocessor", StandardScaler()), ("model", model)])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        r2[name] = r2_score(y_test, y_pred)
        if name == "Lineal":
            coef = pd.Series(pipe.named_steps["model"].coef_, index=X_train.columns)

    return (r2, coef)
