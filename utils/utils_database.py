from datetime import datetime

from faker import Faker

from models.models import Client, User, Contract, Event, Department
from controllers.session import get_session

fake = Faker(locale='fr-FR')

departments = ['Commercial', 'Management', 'Support']
NUMBER_TO_CREATE = 10

users = [
    ['Rémy', 'Reynaud', 'remy.reynaud@epic-events.com', 1],
    ['Benoît', 'Marchal', 'benoit.marchal@epic-events.com', 1],
    ['Jeanne', 'Boutin', 'jeanne.boutin@epic-events.com', 1],
    ['Suzanne', 'Peron', 'suzanne.peron@epic-events.com', 1],
    ['Zoé', 'Colin', 'zoe.colin@epic-events.com', 2],
    ['Patricia', 'Bouchet', 'patricia.bouchet@epic-events.com', 2],
    ['Mathilde', 'Navarro', 'mathilde.navarro@epic-events.com', 2],
    ['Gabriel', 'Briand', 'gabriel.briand@epic-events.com', 2],
    ['Eugène', 'Chevallier', 'eugene.chevallier@epic-events.com', 3],
    ['Henriette', 'Lamy', 'henriette.lamy@epic-events.com', 3]
]

clients = [
    [
        'Gabriel', 'Daniel', 'gabriel.daniel@fabre.com',
        '05.62.43.30.49', 'Fabre', 1
    ],
    [
        'Charlotte', 'Roger', 'charlotte.roger@picard.com',
        '03.22.16.90.63', 'Picard', 3
    ],
    [
        'Nicolas', 'Diaz', 'nicolas.diaz@albert-et-fils.com',
        '01.80.23.32.45', 'Albert et Fils', 2
    ],
    [
        'Luc', 'Delaunay', 'luc.delaunay@bruneau.com',
        '05.33.19.03.83', 'Bruneau', 4
    ],
    [
        'Élise', 'Tanguy', 'elise.tanguy@dumas.com',
        '04.70.54.48.33', 'Dumas', 2
    ],
    [
        'Noël', 'Da Silva', 'noel.dasilva@le-goff.com',
        '03.58.76.69.72', 'Le Goff', 1
    ],
    [
        'Valérie', 'Petitjean', 'valerie.petitjean@rémy-et-fils.com',
        '02.32.26.71.16', 'Rémy et Fils', 3
    ],
    [
        'Nicolas', 'Torres', 'nicolas.torres@gérard.com',
        '05.63.24.86.03', 'Gérard', 1
    ],
    [
        'Richard', 'Grenier', 'richard.grenier@navarro-vasseur.com',
        '07.87.39.58.05', 'Navarro Vasseur SARL', 4
    ],
    [
        'Marthe', 'Merle', 'marthe.merle@nguyen.com',
        '03.52.82.80.92', 'Nguyen', 4
    ]
]

contracts = [
    [1, 1, 72.36, 58.42, Contract.ContractStatus.unsigned],
    [2, 3, 96.44, 89.8, Contract.ContractStatus.unsigned],
    [3, 2, 86.17, 16.56, Contract.ContractStatus.signed],
    [4, 4, 18.58, 16.78, Contract.ContractStatus.unsigned],
    [5, 2, 72.98, 9.41, Contract.ContractStatus.unsigned],
    [6, 1, 21.01, 12.25, Contract.ContractStatus.signed],
    [7, 3, 70.67, 61.03, Contract.ContractStatus.unsigned],
    [8, 1, 50.15, 27.39, Contract.ContractStatus.signed],
    [9, 4, 102.49, 92.7, Contract.ContractStatus.unsigned],
    [10, 4, 66.98, 28.81, Contract.ContractStatus.signed]
]

events = [
    [
        1, 1, datetime(2025, 9, 29, 13, 0, 0),
        datetime(2025, 9, 29, 19, 0, 0),
        'avenue de Fernandez', 17, 'Ceci est une note.'
    ],
    [
        2, 2, datetime(2024, 10, 1, 8, 30, 0),
        datetime(2024, 10, 2, 12, 30, 0),
        '608, chemin Julien Prévost', 94, 'Ceci est une note.'
    ],
    [
        3, 3, datetime(2025, 10, 15, 17, 15, 0),
        datetime(2025, 10, 15, 23, 30, 0),
        '30, boulevard de Blin', 88, 'Ceci est une note.'
    ],
    [
        4, 4, datetime(2024, 10, 17, 15, 0, 0),
        datetime(2024, 10, 17, 17, 30, 0),
        'rue de Joly', 73, 'Ceci est une note.'
    ],
    [
        5, 5, datetime(2024, 9, 28, 12, 45, 0),
        datetime(2024, 9, 28, 14, 45, 0),
        '8, rue Langlois', 47, 'Ceci est une note.'
    ],
    [
        6, 6, datetime(2024, 9, 30, 9, 0, 0),
        datetime(2024, 9, 30, 12, 30, 0),
        '9, rue Gérard', 50, 'Ceci est une note.'
    ],
    [
        7, 7, datetime(2025, 10, 5, 14, 30, 0),
        datetime(2025, 10, 5, 23, 30, 0),
        'rue Suzanne Blanchet', 64, 'Ceci est une note.'
    ],
    [
        8, 8, datetime(2024, 9, 21, 17, 30, 0),
        datetime(2024, 9, 23, 14, 30, 0),
        '46, rue Pineau', 41, 'Ceci est une note.'
    ],
    [
        9, 9, datetime(2024, 4, 8, 6, 45, 0),
        datetime(2024, 4, 8, 19, 0, 0),
        '75, chemin de Voisin', 28, 'Ceci est une note.'
    ],
    [
        10, 10, datetime(2025, 10, 5, 8, 45, 0),
        datetime(2025, 10, 6, 20, 45, 0),
        '79, rue du Moulin', 28, 'Ceci est une note.'
    ]
]


def get_user_test():
    all_users = []
    for user in users:
        user_data = {
            'first_name': user[0],
            'last_name': user[1],
            'email': user[2],
            'password': '12345',
            'department_id': user[3]
        }
        all_users.append(User.create(**user_data))
    return all_users


def get_client_test():
    all_clients = []
    for client in clients:
        all_clients.append(
            Client.create(*client)
        )

    return all_clients


def get_contract_test():
    all_contracts = []
    for contract in contracts:
        all_contracts.append(
            Contract.create(*contract)
        )

    return all_contracts


def get_event_test():
    all_events = []
    for event in events:
        all_events.append(
            Event.create(*event)
        )

    return all_events


def get_department():
    department_names = ['Commercial', 'Support', 'Management']
    all_departments = []
    for name in department_names:
        all_departments.append(
            Department.create(name=name)
        )

    return all_departments


def generate_datas():
    departments = get_department()
    users = get_user_test()
    clients = get_client_test()
    contracts = get_contract_test()
    events = get_event_test()

    all_datas = [departments, users, clients, contracts, events]

    for data in all_datas:
        session = get_session()
        for element in data:
            session.add(element)

        session.commit()
        session.close()
