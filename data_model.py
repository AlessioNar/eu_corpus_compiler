import rdflib
from rdflib import Namespace, URIRef
from rdflib.namespace import NamespaceManager

# Define the FRBR namespace
FRBR = Namespace('http://purl.org/vocab/frbr/core#')

# Create a namespace manager
nsm = NamespaceManager(rdflib.Graph())
nsm.bind('frbr', FRBR)
nsm.bind('owl', rdflib.OWL)
nsm.bind('rdf', rdflib.RDF)
nsm.bind('rdfs', rdflib.RDFS)

class FRBRGraph(rdflib.Graph):
    def __init__(self):
        super().__init__()
        self.bind('frbr', FRBR)
        self.bind('owl', rdflib.OWL)
        self.bind('rdf', rdflib.RDF)
        self.bind('rdfs', rdflib.RDFS)

    def add_work(self, uri, title, creator):
        work = URIRef(uri)
        self.add((work, rdflib.RDF.type, FRBR.Work))
        self.add((work, FRBR.title, title))
        self.add((work, FRBR.creator, creator))

    def add_expression(self, uri, work, title, language):
        expression = URIRef(uri)
        self.add((expression, rdflib.RDF.type, FRBR.Expression))
        self.add((expression, FRBR.realizationOf, work))
        self.add((expression, FRBR.title, title))
        self.add((expression, FRBR.language, language))

    def add_manifestation(self, uri, expression, title, publisher, date):
        manifestation = URIRef(uri)
        self.add((manifestation, rdflib.RDF.type, FRBR.Manifestation))
        self.add((manifestation, FRBR.embodimentOf, expression))
        self.add((manifestation, FRBR.title, title))
        self.add((manifestation, FRBR.publisher, publisher))
        self.add((manifestation, FRBR.date, date))

    def add_item(self, uri, manifestation):
        item = URIRef(uri)
        self.add((item, rdflib.RDF.type, FRBR.Item))
        self.add((item, FRBR.exemplarOf, manifestation))

    def add_person(self, uri, name):
        person = URIRef(uri)
        self.add((person, rdflib.RDF.type, FRBR.Person))
        self.add((person, FRBR.name, name))

    def add_corporate_body(self, uri, name):
        corporate_body = URIRef(uri)
        self.add((corporate_body, rdflib.RDF.type, FRBR.CorporateBody))
        self.add((corporate_body, FRBR.name, name))

class Work:
    def __init__(self, uri, title, creator):
        self.uri = uri
        self.title = title
        self.creator = creator

class Expression:
    def __init__(self, uri, work, title, language):
        self.uri = uri
        self.work = work
        self.title = title
        self.language = language

class Manifestation:
    def __init__(self, uri, expression, title, publisher, date):
        self.uri = uri
        self.expression = expression
        self.title = title
        self.publisher = publisher
        self.date = date

class Item:
    def __init__(self, uri, manifestation):
        self.uri = uri
        self.manifestation = manifestation

class Person:
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name

class CorporateBody:
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name

# Example usage
graph = FRBRGraph()

work = Work('http://example.org/work/1', 'Example Work', 'http://example.org/person/1')
expression = Expression('http://example.org/expression/1', work.uri, 'Example Expression', 'en')
manifestation = Manifestation('http://example.org/manifestation/1', expression.uri, 'Example Manifestation', 'Example Publisher', '2020-01-01')
item = Item('http://example.org/item/1', manifestation.uri)
person = Person('http://example.org/person/1', 'John Doe')
corporate_body = CorporateBody('http://example.org/corporate-body/1', 'Example Corporate Body')

graph.add_work(work.uri, work.title, work.creator)
graph.add_expression(expression.uri, expression.work, expression.title, expression.language)
graph.add_\manifestation(manifestation.uri, manifestation.expression, manifestation.title, manifestation.publisher, manifestation.date)
graph.add_item(item.uri, item.manifestation)
graph.add_person(person.uri, person.name)
graph.add_corporate_body(corporate_body.uri, corporate_body.name)

print(graph.serialize(format='turtle'))