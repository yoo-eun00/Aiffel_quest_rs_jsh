import os
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.model_selection import KFold, cross_val_score


def rmse(y, y_pred):
    return np.sqrt(mean_squared_error(np.expm1(y), np.expm1(y_pred)))


def get_scores(models, X, y):
    df = {}

    for model in models:
        model_name = model.__class__.__name__

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        df[model_name] = rmse(y_test, y_pred)
        score_df = pd.DataFrame(df, index=["RMSE"]).T.sort_values(
            "RMSE", ascending=False
        )

    return score_df


def grid_search_cv(model, train, y, param_grid, verbose=2, n_jobs=5):
    # GridSearchCV 모델로 초기화
    grid_model = GridSearchCV(
        model,
        param_grid=param_grid,
        scoring="neg_mean_squared_error",
        cv=5,
        verbose=verbose,
        n_jobs=n_jobs,
    )

    # 모델 fitting
    grid_model.fit(train, y)

    # 결과값 저장
    params = grid_model.cv_results_["params"]
    score = grid_model.cv_results_["mean_test_score"]

    # 데이터 프레임 생성
    results = pd.DataFrame(params)
    results["score"] = score

    # RMSLE 값 계산 후 정렬
    results["RMSLE"] = np.sqrt(-1 * results["score"])
    results = results.sort_values("RMSLE")

    return results


def get_cv_score(models, x, y):
    """return r-squared score of each model."""
    kfold = KFold(n_splits=5).get_n_splits(x.values)
    for m in models:
        CV_score = np.mean(cross_val_score(m["model"], X=x.values, y=y, cv=kfold))
        print(f"Model: {m['name']}, CV score:{CV_score:.4f}")


def average_blending(models, x, y, sub_x):
    """return regression prediction by averaging models."""
    for m in models:
        m["model"].fit(x.values, y)

    predictions = np.column_stack([m["model"].predict(sub_x.values) for m in models])
    return np.mean(predictions, axis=1)
