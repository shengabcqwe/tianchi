# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import xgboost as xgb
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.metrics import f1_score
from sklearn.model_selection import KFold, GridSearchCV
from logger import ExecuteLogger

logger = ExecuteLogger()
log = logger.get_logger()

# train_feature = pd.read_csv("user_train.csv", encoding="gbk")  # (20000, 189)
# test_feature = pd.read_csv("user_test.csv", encoding="gbk")  # (4000, 189)
train_label = pd.read_csv("./data/df_id_train.csv", header=None)
test_label = pd.read_csv("./data/df_id_test.csv", header=None)
# train_id = pd.read_csv("user_train_id.csv", header=None)
# test_id = pd.read_csv("user_test_id.csv", header=None)
# train_feature = pd.concat([train_id, train_feature], axis=1)
# test_feature = pd.concat([test_id, test_feature], axis=1)

train_feature = pd.read_csv("train.csv", encoding="gbk")
test_feature = pd.read_csv("test.csv", encoding="gbk")

column_name = ["f" + str(i) if i !=0 else "uid" for i in range(train_feature.shape[1])]
train_feature.columns = column_name
test_feature.columns = column_name
train_label.columns = ["uid", "label"]
test_label.columns = ["uid"]

train = train_label.merge(train_feature, on="uid", how="left")
test = test_label.merge(test_feature, on="uid", how="left")
train_x = train.iloc[:, 2:]
train_y = train.iloc[:, 1]
test_x = test.iloc[:, 1:]

d_train = xgb.DMatrix(train_x, label=train_y)
d_test = xgb.DMatrix(train_y)

random_seed = 420

def analyse_n_estimators(model, X, y, est_list=[100, 200, 400, 800, 1600, 3200]):
    k_fold = KFold(n_splits=5, shuffle=True, random_state=random_seed)
    f1_total_train = []
    f1_total_test = []

    for n_estimators in est_list:
        model.set_params(n_estimators=n_estimators)
        f1_list_train = []
        f1_list_test = []

        for i, (train_index, test_index) in enumerate(k_fold.split(X)):
            x_train, x_test = X.iloc[train_index, :], X.iloc[test_index, :]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            model.fit(x_train, y_train)
            pred_train = model.predict(x_train)
            pred_test = model.predict(x_test)
            f1_train = f1_score(y_train, pred_train)
            f1_test = f1_score(y_test, pred_test)
            f1_list_train.append(f1_train)
            f1_list_test.append(f1_test)
            # log.info("[n_estimators {}][Fold {}][Train] f1_score: {}".format(n_estimators, i + 1, f1_train))
            # log.info("[n_estimators {}][Fold {}][Cross validation] f1_score: {}".format(n_estimators, i + 1, f1_test))
            # print("[n_estimators {}][Fold {}][Train] f1_score: {}".format(n_estimators, i + 1, f1_train))
            # print("[n_estimators {}][Fold {}][Cross validation] f1_score: {}".format(n_estimators, i + 1, f1_test))

        f1_train_mean = np.mean(f1_list_train)
        f1_test_mean = np.mean(f1_list_test)
        f1_train_std = np.std(f1_list_train)
        f1_test_std = np.std(f1_list_test)
        f1_total_train.append(f1_list_train)
        f1_total_test.append(f1_list_test)
        print("[n_estimators {}][Train] f1_score mean: {}, std: {}".format(n_estimators, f1_train_mean, f1_train_std))
        print("[n_estimators {}][Cross validation] f1_score mean: {}, std: {}".format(n_estimators, f1_test_mean, f1_test_std))
        log.info("[n_estimators {}][Train] f1_score mean: {}, std: {}".format(n_estimators, f1_train_mean, f1_train_std))
        log.info("[n_estimators {}][Cross validation] f1_score mean: {}, std: {}".format(n_estimators, f1_test_mean, f1_test_std))

    score_train = np.array(f1_total_train).T
    score_test = np.array(f1_total_test).T
    score_train_mean = score_train.mean(axis=0)
    score_test_mean = score_test.mean(axis=0)
    score_train_std = score_train.std(axis=0)
    score_test_std = score_test.std(axis=0)
    plt.figure()
    plt.xlabel("n_estimators")
    plt.ylabel("score")
    plt.plot(range(len(est_list)), score_train_mean, color="b", label="train_score")
    plt.plot(range(len(est_list)), score_test_mean, color="r", label="validation_score")
    plt.fill_between(range(len(est_list)), score_train_mean - score_train_std, score_train_mean + score_train_std, alpha=0.1, color="b")
    plt.fill_between(range(len(est_list)), score_test_mean - score_test_std, score_test_mean + score_test_std, alpha=0.1, color="r")
    plt.xticks(range(len(est_list)), est_list)
    plt.legend()
    plt.grid()
    plt.show()

pos_count = train_label["label"].sum()
scale_pos_weight = (len(train_label) - pos_count) / pos_count


if __name__ == "__main__":
    # # 200个特征最优模型参数 - 封存
    # model = XGBClassifier(max_depth=4,
    #                       min_child_weight=10,
    #                       learning_rate=0.005,
    #                       n_estimators=13000,
    #                       subsample=0.9,  # 0.8
    #                       colsample_bytree=0.8,  # 0.9
    #                       scale_pos_weight=12,  # 10
    #                       objective="reg:logistic",
    #                       nthread=-1,
    #                       seed=random_seed)

    # 270个特征最优模型参数
    model = XGBClassifier(max_depth=4,
                          min_child_weight=10,
                          learning_rate=0.005,
                          n_estimators=12000,
                          subsample=0.9,  # 0.8
                          colsample_bytree=0.8,  # 0.9
                          scale_pos_weight=14,  # 10
                          objective="reg:logistic",
                          nthread=-1,
                          seed=random_seed)

    # analyse_n_estimators(model, train_x, train_y, est_list=[8000, 9000, 10000, 11000, 12000])

    # params = {"max_depth": [3, 4, 5],
    #           "min_child_weight": [1, 10, 100],}
    # params = {"min_child_weight": [5, 7, 9, 10, 11, 13, 15]}
    # params = {"subsample": [0.7, 0.8, 0.9, 1],
    #           "colsample_bytree": [0.7, 0.8, 0.9, 1],}
    # params = {"reg_lambda": [0.1, 1, 10, 100]}
    # params = {"scale_pos_weight": [6, 8, 10, 12, 14, 16, 18]}
    # g_model = GridSearchCV(model, param_grid=params, scoring="f1", cv=5, n_jobs=-1, iid=False, verbose=0)
    # g_model.fit(train_x, train_y)
    # print(g_model.grid_scores_)
    # print(g_model.best_score_)
    # print(g_model.best_params_)
    # log.info("Best parameter is {}, with score {}".format(g_model.best_params_, g_model.best_score_))

    model.fit(train_x, train_y)
    pred = model.predict(test_x)
    test_uid = test.iloc[:, 0]
    result = pd.DataFrame(columns=["uid", "label"])
    result["uid"] = test_uid
    result["label"] = pred
    result.to_csv("result.csv", index=False)
    model.booster().save_model("2.model")