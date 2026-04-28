import pandas as pd
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def prepare_data(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Prepare feature matrix and target vector for regression models.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing all variables.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]
        - X_train : Feature matrix for training
        - X_test : Target vector
        - y_train : Objective matrix for training
        - y_test : Target vector for testing

    Raises
    ------
    ValueError
        If the target column is missing or the DataFrame is empty.

    Notes
    -----
    This function:
    - Removes non-numeric or unwanted columns (e.g., 'ciudad')
    - Separates features and target
    """
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
    """
    Train regression models to predict UHI.

    Parameters
    ----------
        - X_train : pd.DataFrame
            Feature matrix for training
        - X_test : pd.DataFrame
            Target vector
        - y_train : pd.DataFrame
            Objective matrix for training
        - y_test : pd.DataFrame
            Target vector for testing

    Returns
    -------
    tuple[dict, pd.Series]
        Dictionary containing trained models:
        - 'linear': LinearRegression model
        - 'ridge': Ridge regression model
        - 'lasso': Lasso regression model
        Series: the linear regression model coefficients

    Raises
    ------
    ValueError
        If input arrays are empty or have incompatible shapes.

    Notes
    -----
    Three models are trained:
    - Linear Regression: baseline, interpretable
    - Ridge Regression: includes regularization to reduce overfitting
    - Lasso Regression: same as Ridge
    """
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
