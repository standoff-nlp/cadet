import spacy
import numpy as np
from scipy.special import softmax

## Strategies from https://medium.com/@duyanhnguyen_38925/active-learning-uncertainty-sampling-p3-edd1f5a655ac
def least_confident(probs):

    _, n_classes = probs.shape

    return  (1 - (
        (1 - softmax(probs, axis=1).max(axis=1)) 
        * (n_classes/(n_classes-1))
    )).mean() # avg confidence over doc


def margin_of_confidence(probs):

    probs = softmax(probs, axis=1)

    confidence = []
    for irow, (a,b) in enumerate(probs.argsort(axis=1)[:,::-1][:,:2]):
        confidence.append(
            1 - (probs[irow, a] - probs[irow, b])
        )

    return np.array(confidence).mean() # avg confidence over doc


__strategy_lookup = {
    "least confident": least_confident,
    "margin of confidence": margin_of_confidence,
}

def get_component(nlp, t_component_name):

    for component_name, component in nlp.pipeline:
        if component_name == t_component_name:
            return component

    raise KeyError(f"component {t_component_name} not found in pipeline.")


def sample(corpus, nlp, component_name, strategy="least confident"):
    """ Reorder the samples in `corpus` by how confident the given component is with respect to the given strategy.
    """
    component = get_component(nlp, component_name)
    
    _, probs = component.predict(list(nlp.pipe(corpus)))

    confidences = []

    for it_probs in probs:    
        confidences.append(
            __strategy_lookup[strategy](it_probs)
        )

    return [docs for _, docs in sorted(zip(confidences,corpus))], confidences


def example():

    corpus = [
        """Schwäbisch ist eine Dialektgruppe, die im mittleren und südöstlichen Bereich Baden-Württembergs, im Südwesten Bayerns sowie im äußersten Nordwesten Tirols gesprochen wird.""",
        """Die westoberdeutsche (schwäbisch-alemannische) Dialektgruppe. Die hellblau eingefärbten schwäbischen Mundarten bilden eine der großen westoberdeutschen Untergruppen. Linguistisch gesehen gehört Schwäbisch zu den schwäbisch-alemannischen Dialekten und damit zum Oberdeutschen. Von den anderen schwäbisch-alemannischen Dialekten hat es sich durch die vollständige Durchführung der neuhochdeutschen Diphthongierung abgetrennt. „Mein neues Haus“ lautet im Schwäbischen deshalb „Mae nuis Hous“ (je nach Region) und nicht wie in anderen alemannischen Dialekten „Miis nüü Huus“."""
    ]
    
    nlp = spacy.load("de")

    sampling_order, confidences = sample(
        corpus,
        nlp,
        "tagger",
        strategy="margin of confidence"
    )

    for c, s in zip(confidences, sampling_order):
        print(c, s)


if __name__ == "__main__":
    example()
