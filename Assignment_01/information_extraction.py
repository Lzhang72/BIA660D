from __future__ import print_function
import re
import spacy

from pyclausie import ClausIE


nlp = spacy.load('en')
re_spaces = re.compile(r'\s+')


class Person(object):
    def __init__(self, name, likes=None, has=None, travels=None):
        """
        :param name: the person's name
        :type name: basestring
        :param likes: (Optional) an initial list of likes
        :type likes: list
        :param dislikes: (Optional) an initial list of likes
        :type dislikes: list
        :param has: (Optional) an initial list of things the person has
        :type has: list
        :param travels: (Optional) an initial list of the person's travels
        :type travels: list
        """
        self.name = name
        self.likes = [] if likes is None else likes
        self.has = [] if has is None else has
        self.travels = [] if travels is None else travels


class Pet(object):
    def __init__(self, pet_type, name=None):
        self.name = name
        self.type = pet_type


class Trip(object):
    def __init__(self,depart_date, depart_location):
        self.departs_on = depart_date
        self.departs_to = depart_location


persons = []
pets = []
trips = []


def get_data_from_file(file_path='./chatbot_data.txt'):
    with open(file_path) as infile:
        cleaned_lines = [line.strip() for line in infile if not line.startswith(('$$$', '###', '===','\n'))]

    return cleaned_lines


def select_person(name):
    for person in persons:
        if person.name == name:
            return person


def add_person(name):
    person = select_person(name)

    if person is None:
        new_person = Person(name)
        persons.append(new_person)

        return new_person

    return person


def select_pet(name):
    for person in persons:
        if person.name == name:
            return person


def add_pet(type, name=None):
    pet = None

    if name:
        pet = select_pet(name)

    if pet is None:
        pet = Pet(type, name)
        pets.append(pet)

    return pet


def get_persons_pet(person_name):

    person = select_person(person_name)

    for thing in person.has:
        if isinstance(thing, Pet):
            return thing


def get_persons_trip(person_name):
    person = select_person(person_name)

    for thing in person.travels:
        if isinstance(thing,Trip):
            return thing



def select_trip(location):
    for trip in trips:
        if trip.departs_to == location:
            return trip


def add_trip(date,location):
    trip =select_trip(location)

    if trip is None:
        trip = Trip(date,location)
        trips.append(trip)
    return trip

def process_relation_triplet(triplet):
    """
    find relations of types:
    (PERSON, likes, PERSON)
    (PERSON, has, PET)
    (PET, has_name, NAME)
    (PERSON, travels, TRIP)
    (TRIP, departs_on, DATE)
    (TRIP, departs_to, PLACE)
    :param triplet: The relation triplet from ClausIE
    :type triplet: tuple
    :return: a triplet in the formats specified above
    :rtype: tuple
    """

    sentence = triplet.subject + ' ' + triplet.predicate + ' ' + triplet.object

    doc = nlp(unicode(sentence))
    global root

    for t in doc:
        if t.pos_ == 'VERB' and t.head == t:
            root = t
        # elif t.pos_ == 'NOUN'

    # also, if only one sentence
    # root = doc[:].root


    """
    CURRENT ASSUMPTIONS:
    - People's names are unique (i.e. there only exists one person with a certain name).
    - Pet's names are unique
    - The only pets are dogs and cats
    - Only one person can own a specific pet
    - A person can own only one pet
    - The vehicle for travel is airplane
    """


    # Process (PERSON, likes, PERSON) relations
    if root.lemma_ == 'like':
        if triplet.subject in [e.text for e in doc.ents if e.label_ in ['PERSON','ORG']] and triplet.object in [e.text for e in doc.ents if e.label_ in ['PERSON']]:
            s = add_person(triplet.subject)
            o = add_person(triplet.object)
            s.likes.append(o)

    if root.lemma_ == 'be' and triplet.object.startswith('friends with'):
        fw_who_list = []
        for t in triplet.object.split(' '):
            t_doc = nlp(unicode(t))
            if t_doc[0].pos_ == 'PROPN':
                fw_who_list.append(t)


        for i in range(len(fw_who_list)):
            fw_who = fw_who_list[i]
            if triplet.subject in [e.text for e in doc.ents if e.label_ == 'PERSON']:
                s = add_person(triplet.subject)
                o = add_person(fw_who)
                s.likes.append(o)
                o.likes.append(s)

    if root.lemma_ == 'be' and triplet.object == 'friends':
        fw_ea_doc = nlp(unicode(triplet.subject))
        fw_ea_list = [t.text for t in fw_ea_doc if t.pos_== 'PROPN']
        if len(fw_ea_list) == 2:
            s = add_person(fw_ea_list[0])
            o = add_person(fw_ea_list[1])
            s.likes.append(o)
            o.likes.append(s)

    # Process (PET, has, NAME)
    if triplet.subject.endswith('name') and ('dog' in triplet.subject or 'cat' in triplet.subject):
        obj_span = doc.char_span(sentence.find(triplet.object), len(sentence))

        # handle single names, but what about compound names? Noun chunks might help.
        if obj_span[0].pos_ == 'PROPN': #len(obj_span) == 1
            name = triplet.object
            subj_start = sentence.find(triplet.subject)
            subj_doc = doc.char_span(subj_start, subj_start + len(triplet.subject))

            s_people = [token.text for token in subj_doc if token.ent_type_ == 'PERSON']

            assert len(s_people) == 1
            s_person = add_person(s_people[0])
            #s_person = select_person(s_people[0])

            s_pet_type = 'dog' if 'dog' in triplet.subject else 'cat'

            pet = add_pet(s_pet_type, name)

            s_person.has.append(pet)

    if root.lemma_ == 'have' and ('dog' in triplet.object or 'cat' in triplet.object) and 'named'in triplet.object:
        s = add_person(triplet.subject)
        named_doc = nlp(unicode(triplet.object))
        name_t = [t for t in named_doc if t.text == 'named'][0]
        name_what = [t for t in name_t.children][0].text
        s_pet_type = 'dog' if 'dog' in triplet.object else 'cat'
        pet = add_pet(s_pet_type,name_what)
        s.has.append(pet)

    # process (Person, travel, Date, destination)#'PERSON' in [str(token.ent_type_ for token in triplet.subject)]:
    if root.lemma_ in ['fly','take','leave','go','travel']:
        travel_doc = nlp(unicode(triplet.object))
        travel_des_list = [e.text.lower() for e in travel_doc.ents if e.label_ == 'GPE']
        if len(travel_des_list) != 0:
            travel_des = travel_des_list[0]
            travel_date_list = [e.text for e in travel_doc.ents if e.label_ == 'DATE']
            if len(travel_date_list) != 0:
                travel_date = travel_date_list[0]
                trip = add_trip(travel_date,travel_des)
                doc_subject = nlp(unicode(triplet.subject))
                s_people = [token.text for token in doc_subject if token.ent_type_ == 'PERSON' or token.text == 'Sally']
                for s_traveler in s_people:
                    traveler = add_person(s_traveler)
                    traveler.travels.append(trip)












def preprocess_question(question):
    #remove 's
    question = question.replace('\'s','')
    question = question.replace('ing','')

    # remove articles: a, an, the

    q_words = question.split(' ')

    # when won't this work?
    for article in ('a', 'an', 'the','is','are','to','When','when', 'of'):
        try:
            q_words.remove(article)
        except:
            pass

    return re.sub(re_spaces, ' ', ' '.join(q_words))


def has_question_word(string):
    # note: there are other question words
    for qword in ('who', 'what','when','does'):
        if qword in string.lower():
            return True

    return False







def main():
    sents = get_data_from_file()

    cl = ClausIE.get_instance()

    triples = cl.extract_triples(sents)

    for t in triples:
        #print(t.subject,'$$',t.predicate,'$$',t.object)
        process_relation_triplet(t)



def answer_question(question_string):
    cl = ClausIE.get_instance()
    question = question_string
    while question[-1] != '?':
        question = raw_input("Please enter your question: ")

        if question[-1] != '?':
            print('This is not a question... please try again')
    #print([preprocess_question(question)])

    q_trip = cl.extract_triples([preprocess_question(question)])[0]
    answers = []


    # (WHO, has, PET)
    # answer for pets
    if q_trip.subject.lower() == 'who' and q_trip.object in [pet.type for pet in pets]:
        answer = '{} has a {} named {}.'

        if q_trip.object == 'dog':
            for person in persons:
                pet = get_persons_pet(person.name)
                if pet and pet.type == 'dog':
                    answers.append(answer.format(person.name, 'dog', pet.name))

        if q_trip.object == 'cat':
            for person in persons:
                pet = get_persons_pet(person.name)
                if pet and pet.type == 'cat':
                    answers.append(answer.format(person.name, 'cat', pet.name))

    # who travel to someplace
    if q_trip.subject.lower() == 'who' and q_trip.predicate in ['going', 'flying', 'traveling', 'visiting','go','fly','travel','visit']:
        answer = '{} travel to {} in {}'
        trip = select_trip(q_trip.object.lower())
        for person in persons:
            if trip in person.travels:
                answers.append(answer.format(person.name, q_trip.object, trip.departs_on))

    # who like whom
    if q_trip.subject.lower() == 'who' and q_trip.predicate in ['likes']:
        answer = '{} {} {}'
        beliked = select_person(q_trip.object)

        if beliked:
            for person in persons:
                if beliked in person.likes:
                    answers.append(answer.format(person.name, q_trip.predicate, q_trip.object))



    if q_trip.subject[0:4] == ('Does') or q_trip.subject[0:4] == ('does') and q_trip.predicate == 'like':
        ob_person = select_person(q_trip.object)
        sub_person = select_person(q_trip.subject[5:])
        if ob_person and sub_person:
            if ob_person in sub_person.likes:
                answers.append('Yes')
            else:
                answers.append('No')


    if q_trip.predicate == 'does like' and q_trip.object.lower() == 'who':
        person_ = select_person(q_trip.subject)
        if person_:
            for n in person_.likes:
                answers.append(n.name)


    # when to travel
    if question[0:4] in ['when', 'When'] and q_trip.predicate in ['be flying', 'be traveling', 'be going','flying', 'traveling', 'going','go','travel','fly']:
        sub_person = select_person(q_trip.subject)
        answer = 'depart on {}'
        des_ = select_trip(q_trip.object.lower())
        if sub_person and des_:
            if des_ in sub_person.travels:
                answers.append(answer.format(des_.departs_on))

    #get someone's pet
    if q_trip.subject in ['what','What'] and q_trip.predicate == 'name':
        if 'dog' in q_trip.object:
            answer = '{}\'s {}\'s name is {}'
            object_doc = nlp(unicode(q_trip.object))
            person_ = select_person([t.text for t in object_doc if t.pos_ in ['PROPN']][0])
            pet = person_.has[0]
            if pet.type == 'dog':
                answers.append(answer.format(person_.name, pet.type, pet.name))

        if 'cat' in q_trip.object:
            answer = '{}\'s {}\'s name is {}'
            object_doc = nlp(unicode(q_trip.object))
            person_ = select_person([t.text for t in object_doc if t.pos_ in ['PROPN']][0])
            pet = person_.has[0]
            if pet.type == 'cat':
                answers.append(answer.format(person_.name, pet.type, pet.name))


    if len(answers) != 0 :
        for a in answers:
            print(a)
    else:
        print('sorry, I do not know')




def process_data_from_input_file():
    #if __name__ == '__main__':
    main()

