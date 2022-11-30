# Sakey chart

# Get all unique nodes

# Noun and emotion link
sankey_labels = {}
sankey_values = {}
for index, row in df_filtered.iterrows():
    emotion = 'E/' + row['emotion1']

    sankey_labels[emotion] = sankey_labels.get(
        emotion, len(sankey_labels.keys()))

    for topic in row['noun_keyphrases']:
        topic = 'T/' + topic
        sankey_labels[topic] = sankey_labels.get(
            topic, len(sankey_labels.keys()))
        key = (topic, emotion)
        sankey_values[key] = sankey_values.get(key, 0) + 1

    for verb in row['verbs']:
        verb = 'V/' + verb
        sankey_labels[verb] = sankey_labels.get(
            verb, len(sankey_labels.keys()))
        key = (emotion, verb)
        sankey_values[key] = sankey_values.get(key, 0) + 1

    for adj in row['adjectives']:
        adj = 'A/' + adj
        sankey_labels[adj] = sankey_labels.get(adj, len(sankey_labels.keys()))
        key = (emotion, adj)
        sankey_values[key] = sankey_values.get(key, 0) + 1

layout = go.Layout(
    autosize=False,
    height=1500,
    width=1000
)
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=15,
        thickness=10,
        line=dict(color="black", width=0.5),
        label=[x[2:] for x in sankey_labels.keys()],
        color="blue"
    ),
    link=dict(
        # indices correspond to labels, eg A1, A2, A1, B1, ...
        source=[sankey_labels[label] for label, _ in sankey_values.keys()],
        target=[sankey_labels[label] for _, label in sankey_values.keys()],
        value=list(sankey_values.values())
    ))], layout=layout)

fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
st.plotly_chart(fig)
