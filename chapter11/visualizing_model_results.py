"""
Visualizing the results of a classification model in stramlit.
"""
import numpy as np
import pandas as pd
import altair as alt
import streamlit as st

from sklearn.datasets import (
    load_iris,
    load_wine,
    fetch_covtype
)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
)
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import roc_auc_score
from sklearn.metrics import classification_report


dataset_lookup = {
    'Iris': load_iris,
    'Wine': load_wine,
    'Covertype': fetch_covtype,
}


@st.cache
def load_data(name):
    iris = dataset_lookup[name]()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.33, random_state=42
    )
    feature_names = getattr(
        iris, 'feature_names',
        [str(i) for i in range(X_train.shape[1])]
    )
    target_names = getattr(
        iris, 'target_names',
        [str(i) for i in np.unique(iris.target)]
    )
    return (
        X_train, X_test, y_train, y_test,
        target_names, feature_names
    )


@st.cache
def train_model(dataset_name, model_name, n_estimators, max_depth):
    model = [m for m in models if m.__class__.__name__ == model_name][0]
    with st.spinner('Building a {} model for {} ...'.format(
            model_name, dataset_name
    )):
        return model.fit(X_train, y_train)


# sidebar:
st.sidebar.title('Model and dataset selection')
dataset_name = st.sidebar.selectbox(
    'Dataset',
    list(dataset_lookup.keys())
)
(X_train, X_test, y_train, y_test,
 target_names, feature_names) = load_data(dataset_name)

n_estimators = st.sidebar.slider(
    'n_estimators',
    1, 100, 25
)
max_depth = st.sidebar.slider(
    'max_depth',
    1, 150, 10
)
models = [
    DecisionTreeClassifier(max_depth=max_depth),
    RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth
    ),
    ExtraTreesClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth
    ),
]
model_name = st.sidebar.selectbox(
    'Model',
    [m.__class__.__name__ for m in models]
)
model = train_model(dataset_name, model_name, n_estimators, max_depth)


# main content:
st.title('{model} on {dataset}'.format(
    model=model_name,
    dataset=dataset_name
))

predictions = model.predict(X_test)
probs = model.predict_proba(X_test)
st.subheader('Model performance in test')
st.write('AUC: {:.2f}'.format(
    roc_auc_score(
        y_test, probs,
        multi_class='ovo' if len(target_names) > 2 else 'raise',
        average='macro' if len(target_names) > 2 else None
    )
))
st.write(
    pd.DataFrame(
        classification_report(
            y_test, predictions,
            target_names=target_names,
            output_dict=True
        )
    )
)
test_df = pd.DataFrame(
    data=np.concatenate([
        X_test,
        y_test.reshape(-1, 1),
        predictions.reshape(-1, 1)
    ], axis=1),
    columns=feature_names + [
        'target', 'predicted'
    ]
)
target_map = {i: n for i, n in enumerate(target_names)}
test_df.target = test_df.target.map(target_map)
test_df.predicted = test_df.predicted.map(target_map)
confusion_matrix = pd.crosstab(
    test_df['target'],
    test_df['predicted'],
    rownames=['Actual'],
    colnames=['Predicted']
)
st.subheader('Confusion Matrix')
st.write(confusion_matrix)


def highlight_error(s):
    if s.predicted == s.target:
        return ['background-color: None'] * len(s)
    return ['background-color: red'] * len(s)


if st.checkbox('Show test data'):
    st.subheader('Test data')
    st.write(test_df.style.apply(highlight_error, axis=1))


if st.checkbox('Show test distributions'):
    st.subheader('Distributions')
    row_features = feature_names[:len(feature_names)//2]
    col_features = feature_names[len(row_features):]
    test_df_with_error = test_df.copy()
    test_df_with_error['error'] = test_df.predicted == test_df.target
    chart = alt.Chart(test_df_with_error).mark_circle().encode(
            alt.X(alt.repeat("column"), type='quantitative'),
            alt.Y(alt.repeat("row"), type='quantitative'),
            color='error:N'
    ).properties(
            width=250,
            height=250
    ).repeat(
        row=row_features,
        column=col_features
    ).interactive()
    st.write(chart)