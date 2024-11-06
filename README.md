# Projet Epic-Events
OC | Projet 12 - Développez une architecture back-end sécurisée avec Python et SQL.

## Installation

### Clonez le dépôt

Pour cloner le dépôt, vous devrez ouvrir le terminal et effectuer la commande suivante dans le dossier de votre choix :
```bash
git clone https://github.com/Fibuc/Epic-Events.git
```
Ensuite déplacez-vous dans le dossier créé par le clonage nommé `Epic-Events` avec la commande suivante :

```bash
cd Epic-Events
```

### Installation de l'environnement

Dans ce projet nous utilisons **virtualenv** afin de créer notre environnement virtuel.

Ouvrez le terminal et rendez-vous dans le dossier du dépôt local du projet, puis tapez la commande suivante :

```bash
virtualenv .
```

#### Activez votre environnement virtuel

Pour activer votre environnement virtuel, la méthode est différente selon votre système d'exploitation.

##### Linux & MacOS :
```bash
source bin/activate
```
##### Windows : 

CMD :
```bash
Scripts\activate.bat
```

PowerShell :
```bash
Scripts\activate.ps1
```

Veillez également à bien vous situer sur la branche "main" lors de l'exécution du CRM.

### Installez les packages

Lorsque vous aurez activé votre environnement virtuel, vous aurez également besoin d'installer les packages essentiels pour le lancement disponibles dans le requirements.txt.

```bash
pip install -r requirements.txt
```

### Installation de MySQL.

Dans ce projet, nous utilisons MySQL concernant la base de données. Si vous ne l'avez pas, vous pouvez suivre ce [tutoriel OpenClassrooms](https://openclassrooms.com/fr/courses/6971126-implementez-vos-bases-de-donnees-relationnelles-avec-sql/7152681-installez-le-sgbd-mysql) pour l'installation de celui-ci.

## Utilisation du CRM

### La base de données

Tout d'abord, occupons-nous de la base de données car c'est la chose la plus importante. Pas de base, pas de CRM, pas de CRM, ... pas de CRM.

On va donc créer notre base de données via une commande déjà présente dans notre application.

```bash
python epicevents.py createdatabase --datas
```

Cette commande vous permet de créer une base de données avec des valeurs initiales qui seront créées à titre d'exemple. Si vous désirez une base avec des tables vierges, alors supprimez simplement l'option *`--datas`*.

### Les différents utilisateurs pour tester les fonctions

| Nom               | Email                             | Mot de passe | Départment  |
| :-----------------|:----------------------------------|:------------:|:------------|
| Bouchet Patricia  | patricia.bouchet@epic-events.com  | 12345        | Support     |
| Boutin Jeanne     | jeanne.boutin@epic-events.com     | 12345        | Commercial  |
| Briand Gabriel    | gabriel.briand@epic-events.com    | 12345        | Support     |
| Chevallier Eugène | eugene.chevallier@epic-events.com | 12345        | Management  |
| Colin Zoé         | zoe.colin@epic-events.com         | 12345        | Support     |
| Lamy Henriette    | henriette.lamy@epic-events.com    | 12345        | Management  |
| Marchal Benoît    | benoit.marchal@epic-events.com    | 12345        | Commercial  |
| Navarro Mathilde  | mathilde.navarro@epic-events.com  | 12345        | Support     |
| Peron Suzanne     | suzanne.peron@epic-events.com     | 12345        | Commercial  |
| Reynaud Rémy      | remy.reynaud@epic-events.com      | 12345        | Commercial  |

### Les différentes commandes disponibles

***⚠️ Important : Toutes les options des commandes ne sont pas énumérées ici. Si vous souhaitez vérifier toutes les options disponibles concernant une commande, vous pouvez vous y référer en précisant l'option `--help` à la fin de celle-ci.***


| Commandes                             | Informations                   |
| :------------------------------------ |:------------------------------ |
| `python epicevents.py createdatabase` | Crée la base de données.       |
| `python epicevents.py login`          | Se connecte au CRM             |
| `python epicevents.py logout`         | Se déconnecte du CRM           |
| `python epicevents.py users`          | Menu des utilisateurs          |
| * ⮩ `list`                            | - Lister tous les utilisateurs |
| * ⮩ `create`                          | - Créer un utilisateur         |
| * ⮩ `modify`                          | - Modifier un utilisateur      |
| * ⮩ `delete`                          | - Supprimer un utilisateur     |
| `python epicevents.py clients`        | Menu des clients               |
| * ⮩ `list`                            | - Lister tous les clients      |
| * ⮩ `create`                          | - Créer un client              |
| * ⮩ `modify`                          | - Modifier un client           |
| `python epicevents.py contracts`      | Menu des contrats              |
| * ⮩ `list`                            | - Lister tous les contrats     |
| * ⮩ `create`                          | - Créer un contrat             |
| * ⮩ `modify`                          | - Modifier un contrat          |
| `python epicevents.py events`         | Menu des événements            |
| * ⮩ `list`                            | - Lister tous les événements   |
| * ⮩ `create`                          | - Créer un événement           |
| * ⮩ `modify`                          | - Modifier un événement        |


## Générez un rapport flake8

L'application a été contrôlée par Flake8. Vous trouverez le rapport en ouvrant le fichier `index.html` se trouvant dans le dossier `flake8_rapport`.

Pour générer un nouveau rapport flake8 de l'application en format HTML, vous devrez ouvrir votre terminal et vous rendre à la racine de l'application puis utiliser la fonction suivante:

```bash
flake8 --format=html --htmldir=flake8_rapport
```

Ce nouveau rapport sera généré dans le dossier "flake8_rapport".

## Afficher la couverture de test

L'application est couverte par des tests unitaires. Pour effectuer les tests, vous pouvez utiliser la commande suivante:

```bash
pytest tests/
```

Si vous souhaitez afficher la couverture de test, vous pouvez utiliser la commande suivante:

```bash
pytest --cov=. tests/
```

Pour générer un rapport HTML de cette couverture, utilisez la commande suivante:

```bash
pytest --cov=. --cov-report=html tests/
```

