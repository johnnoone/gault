from gault.pipelines import Pipeline


def test_spread_document(subtests):
    pipeline = Pipeline.documents(
        {"id": 1},
        {"id": 2},
        {"id": 3},
    )
    result = pipeline.build()
    assert result == [
        {
            "$documents": [
                {"id": 1},
                {"id": 2},
                {"id": 3},
            ]
        },
    ]


def test_list_documents(subtests):
    pipeline = Pipeline.documents(
        [
            {"id": 1},
            {"id": 2},
            {"id": 3},
        ]
    )
    result = pipeline.build()
    assert result == [
        {
            "$documents": [
                {"id": 1},
                {"id": 2},
                {"id": 3},
            ]
        },
    ]
