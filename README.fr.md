<p align="center">
<img width="300" height="280"
src="screenshots/Trapheus.png">
</p>
<p align="center">
<b>Restore RDS instances in AWS without worrying about client downtime or configuration retention.</b><br/>
<sub>Trapheus can restore individual RDS instance or a RDS cluster.
Modelled as a state machine, with the help of AWS step functions, Trapheus restores the RDS instance in a much faster way than the usual SQL dump preserving the same instance endpoint and confgurations as before.
</sub>
</p>
<p align="center"><a href="https://circleci.com/gh/intuit/Trapheus"><img src="https://circleci.com/gh/intuit/Trapheus.svg?style=svg" alt="TravisCI Build Status"/></a>
<a href = "https://coveralls.io/github/intuit/Trapheus?branch=master"><img src= "https://coveralls.io/repos/github/intuit/Trapheus/badge.svg?branch=master" alt = "Coverage"/></a>
  <a href="http://www.serverless.com"><img src="http://public.serverless.com/badges/v3.svg" alt="serverless badge"/></a>
  <a href="https://github.com/intuit/Trapheus/releases"><img src="https://img.shields.io/github/v/release/intuit/trapheus.svg" alt="release badge"/></a>
</p>

<img src="https://ch-resources.oss-cn-shanghai.aliyuncs.com/images/lang-icons/icon128px.png" width="22px" />[Anglais](README.md)\|[Chinois simplifié](./docs/README.zh-CN.md)\|[français](./docs/README.fr.md)

-   **Important:**cette application utilise divers services AWS et des coûts sont associés à ces services après l'utilisation de l'offre gratuite - veuillez consulter le[Page de tarification AWS](https://aws.amazon.com/pricing/)pour plus de détails.

[![\---------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#table-of-contents)

## Table des matières

-   [➤ Prérequis](#pre-requisites)
-   [➤ Paramètres](#parameters)
-   [➤ Instructions](#instructions)
-   [➤ Exécution](#execution)
-   [➤ Comment ça marche](#how-it-works)
-   [➤ Contribuer à Trapheus](#contributing-to-trapheus)
-   [➤ Contributeurs](#contributors)

[![\---------------------------------------------------------------------------------------------------------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#pre-requisites)

## Conditions préalables

L'application nécessite que les ressources AWS suivantes existent avant l'installation :

1.  `python3.7`installé sur la machine locale suivante[ce](https://www.python.org/downloads/).

2.  Configurer[AWS SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/event-publishing-create-configuration-set.html)
    -   Configurez l'e-mail de l'expéditeur et du destinataire SES ([SES Console](https://console.aws.amazon.com/ses/)->Adresses e-mail).
        -   Une alerte par courrier électronique SES est configurée pour informer l'utilisateur de toute défaillance de la machine à états. Le paramètre email de l'expéditeur est nécessaire pour configurer l'ID de messagerie via lequel l'alerte est envoyée. Le paramètre email du destinataire est nécessaire pour définir l’ID de messagerie auquel l’alerte est envoyée.

3.  Créez le compartiment S3 dans lequel le système va stocker les modèles de formation de nuages :
    -   Nom proposé : trapheus-cfn-s3-[identifiant de compte-]-[région]. Il est recommandé que le nom contienne votre :
        -   identifiant de compte, car les noms de compartiment doivent être globaux (empêche quelqu'un d'autre d'avoir le même nom)
        -   région, pour suivre facilement lorsque vous avez des compartiments trapheus-s3 dans plusieurs régions

4.  Un VPC (spécifique à la région). Le même VPC/région doit être utilisé à la fois pour la ou les instances RDS, à utiliser dans Trapheus, et pour les lambdas de Trapheus.
    -   Considération de sélection de région. Régions prenant en charge :
        -   [Réception d'email](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/regions.html#region-receive-email). Vérifier[Paramètres](#parameters)-> 'RecipientEmail' pour en savoir plus.
    -   Exemple de configuration minimale d'un VPC :
        -   Console VPC :
            -   nom : Trapheus-VPC-[région]\(spécifie le[région]où votre VPC est créé - pour suivre facilement lorsque vous avez des Trapheus-VPC dans plusieurs régions)
            -   [Bloc CIDR IPv4](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html#vpc-sizing-ipv4): 10.0.0.0/16
        -   Console VPC->Page Sous-réseaux et créez deux sous-réseaux privés :
            -   Sous-réseau 1 :
                -   VPC : Trapheus-VPC-[région]
                -   Zone de disponibilité : choisissez-en une
                -   Bloc CIDR IPv4 : 10.0.0.0/19
            -   Sous-réseau2 :
                -   VPC : Trapheus-VPC-[région]
                -   Zone de disponibilité : choisissez-en une différente de celle du sous-réseau 1 AZ.
                -   Bloc CIDR IPv4 : 10.0.32.0/19
        -   Vous avez créé un VPC avec seulement deux sous-réseaux privés. Si vous créez des sous-réseaux non privés, cochez[le rapport entre les sous-réseaux privés et publics, le sous-réseau privé avec une liste de contrôle d'accès réseau personnalisée dédiée et la capacité de réserve](https://aws-quickstart.github.io/quickstart-aws-vpc/).


5.  Une ou plusieurs instances d'une base de données RDS que vous souhaitez restaurer.
    -   Exemple minimal_gratuit_Configuration RDS :
        -   Options du moteur : MySQL
        -   Modèles : niveau gratuit
        -   Paramètres : entrez le mot de passe
        -   Connectivité : VPC : Trapheus-VPC-[région]

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#parameters)

## Paramètres

Voici les paramètres de création du modèle cloudformation :

1.  `--s3-bucket`:[Facultatif]Le nom du compartiment S3 du modèle CloudFormation du[Conditions préalables](#pre-requisites).
2.  `vpcID`:[Requis]L'identifiant du VPC du[Conditions préalables](#pre-requisites). Les lambdas de la machine à états Trapheus seront créés dans ce VPC.
3.  `Subnets`:[Requis]Une liste d'identifiants de sous-réseau privés (spécifiques à la région) séparés par des virgules[Conditions préalables](#pre-requisites)VPC.
4.  `SenderEmail`:[Requis]L'email d'envoi SES configuré dans le[Conditions préalables](#pre-requisites)
5.  `RecipientEmail`:[Requis]Liste séparée par des virgules des adresses e-mail des destinataires configurées dans[Conditions préalables](#pre-requisites).
6.  `UseVPCAndSubnets`:[Facultatif]S'il faut utiliser le vpc et les sous-réseaux pour créer un groupe de sécurité et lier le groupe de sécurité et le vpc aux lambdas. Lorsque UseVPCAndSubnets est laissé de côté (par défaut) ou défini sur « true », les lambdas sont connectés à un VPC dans votre compte et, par défaut, la fonction ne peut pas accéder au RDS (ou à d'autres services) si le VPC ne fournit pas d'accès (soit par acheminer le trafic sortant vers un[Passerelle NAT](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)dans un sous-réseau public, ou avoir un[Point de terminaison d'un VPC](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints.html), qui entraînent tous deux des coûts ou nécessitent une configuration supplémentaire). S'il est défini sur « false », le[lambdas s'exécutera dans un VPC par défaut appartenant à Lambda qui a accès à RDS (et à d'autres services AWS)](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html#vpc-internet).
7.  `SlackWebhookUrls`:[Facultatif]Liste de webhooks Slack séparés par des virgules pour les alertes d'échec.

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#instructions)

## Instructions

### Installation

#### Pour configurer le Trapheus dans votre compte AWS, suivez les étapes ci-dessous :

1.  Cloner le dépôt Trapheus Git
2.  Configuration des informations d'identification AWS. Trapheus utilise boto3 comme bibliothèque client pour communiquer avec Amazon Web Services. Ne hésitez pas à[utiliser n'importe quelle variable d'environnement](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables)que boto3 prend en charge pour fournir des informations d'authentification.
3.  Courir`pip install -r requirements.txt`pour installer le graphe de dépendances
4.  Courir`python install.py`

<p align="center"><img src="screenshots/Trapheus.gif?raw=true"/></p>

> Vous êtes toujours confronté à un problème ? Vérifier la[Problèmes](https://github.com/intuit/Trapheus/issues)section ou ouvrir un nouveau numéro

Ce qui précède configurera un CFT dans votre compte AWS avec le nom fourni lors de l'installation.

**A NOTER**:
Le CFT crée les ressources suivantes :

1.  **DBRestoreStateMachine**Machine à états de fonction étape
2.  Plusieurs lambdas pour exécuter différentes étapes dans la machine à états
3.  LambdaExecutionRole : utilisé dans tous les lambdas pour effectuer plusieurs tâches sur RDS
4.  StatesExecutionRole : rôle IAM avec des autorisations pour exécuter la machine d'état et appeler des lambdas
5.  Compartiment S3 : rds-snapshots-&lt;your_account_id> où les instantanés seront exportés
6.  Clé KMS : est requise pour démarrer la tâche d'exportation de l'instantané vers s3
7.  DBRestoreStateMachineEventRule : une règle Cloudwatch à l'état désactivé, qui peut être utilisée comme ci-dessus[instructions](#to-set-up-the-step-function-execution-through-a-scheduled-run-using-cloudwatch-rule-follow-the-steps-below)basé sur les besoins de l'utilisateur
8.  CWEventStatesExecutionRole : rôle IAM utilisé par la règle DBRestoreStateMachineEventRule CloudWatch, pour permettre l'exécution de la machine d'état depuis CloudWatch

#### Pour configurer l'exécution de la fonction étape par étape via une exécution planifiée à l'aide de la règle CloudWatch, suivez les étapes ci-dessous :

1.  Accédez à la section DBRestoreStateMachineEventRule dans le template.yaml du dépôt Trapheus.
2.  Nous l'avons défini comme règle cron programmée pour qu'elle s'exécute tous les VENDREDI à 8h00 UTC. Vous pouvez le modifier selon votre fréquence de programmation préférée en mettant à jour le**ExpressionHoraire**la valeur de la propriété en conséquence. Exemples:

    -   Pour l'exécuter tous les 7 jours,`ScheduleExpression: "rate(7 days)"`
    -   Pour l'exécuter tous les VENDREDI à 8h00 UTC,`ScheduleExpression: "cron(0 8 ? * FRI *)"`

    Cliquez sur[ici](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)pour tous les détails sur la façon de définir ScheduleExpression.
3.  Exemples de cibles données dans le fichier modèle sous**Cibles**la propriété pour votre référence doit être mise à jour :

    un. Changement**Saisir**propriété en fonction des valeurs de votre propriété d'entrée, donnez en conséquence un meilleur identifiant pour votre cible en mettant à jour le**Identifiant**propriété.

    b. En fonction du nombre de cibles pour lesquelles vous souhaitez définir la planification, ajoutez ou supprimez les cibles.
4.  Changer la**État**valeur de la propriété à**ACTIVÉ**
5.  Enfin, emballez et redéployez la pile en suivant les étapes 2 et 3 dans[Configuration de l'escalier](#to-setup-the-trapheus-in-your-aws-account-follow-the-steps-below)

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#execution)

## Exécution

Pour exécuter la fonction étape, suivez les étapes ci-dessous :

1.  Accédez à la définition de la machine d'état à partir du_Ressources_dans la pile cloudformation.
2.  Cliquer sur_Démarrer l'exécution_.
3.  Sous_Saisir_, fournissez le json suivant comme paramètre :


    {
        "identifier": "<identifier name>",
        "task": "<taskname>",
        "isCluster": true or false
    }

un.`identifier`: (Obligatoire - Chaîne) L'instance RDS ou l'identifiant de cluster qui doit être restauré. Tout type d'instance RDS ou de clusters Amazon Aurora est pris en charge.

b.`task`: (Obligatoire - Chaîne) Les options valides sont`create_snapshot`ou`db_restore`ou`create_snapshot_only`.

c.`isCluster`: (Obligatoire - Booléen) Définir sur`true`si l'identifiant fourni est celui d'un cluster, sinon défini sur`false`

La machine à états peut effectuer l'une des tâches suivantes :

1.  si`task`est réglé sur`create_snapshot`, la machine d'état crée/met à jour un instantané pour l'instance ou le cluster RDS donné à l'aide de l'identifiant de l'instantané :_identifier_-instantané puis exécute le pipeline
2.  si`task`est réglé sur`db_restore`, la machine d'état effectue une restauration sur l'instance RDS donnée, sans mettre à jour un instantané, en supposant qu'il existe un instantané avec un identifiant :_identifier_-instantané
3.  si`task`est réglé sur`create_snapshot_only`, la machine d'état crée/met à jour un instantané pour l'instance ou le cluster RDS donné à l'aide de l'identifiant de l'instantané :_identifier_-instantané et il n'exécuterait pas le pipeline

**Considérations relatives aux coûts**

Une fois le développement ou l'utilisation de l'outil terminé :

1.  si vous n'avez pas besoin de l'instance RDS lorsque vous ne codez pas ou n'utilisez pas l'outil (par exemple, s'il s'agit d'un RDS de test), envisagez d'arrêter ou de supprimer la base de données. Vous pouvez toujours le recréer quand vous en avez besoin.
2.  si vous n'avez pas besoin des anciens modèles Cloud Formation, il est recommandé de vider le compartiment CFN S3.

**Démolir**

Pour démonter votre application et supprimer toutes les ressources associées à la machine d'état Trapheus DB Restore, procédez comme suit :

1.  Connectez-vous à[Console Amazon CloudFormation](https://console.aws.amazon.com/cloudformation/home?#)et trouvez la pile que vous avez créée.
2.  Supprimez la pile. Notez que la suppression de la pile échouera si le compartiment rds-snapshots-&lt;YOUR_ACCOUNT_NO> s3 n'est pas vide, supprimez donc d'abord les exportations d'instantanés dans le compartiment.
3.  Supprimez les ressources AWS du[Conditions préalables](#pre-requisites). La suppression de SES, du compartiment CFN S3 (videz-le si vous ne le supprimez pas) et de VPC est facultative car vous ne verrez pas les frais, mais vous pourrez les réutiliser plus tard pour un démarrage rapide.

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#how-it-works)

## Comment ça fonctionne

**Pipeline complet**

![DBRestore depiction](screenshots/restore_state_machine.png)

Modélisées comme une machine à états, différentes étapes du flux telles que la création/mise à jour d'instantanés, le renommage de l'instance, la restauration et la suppression, l'état d'achèvement/d'échec de chaque opération, l'alerte par e-mail d'échec, etc. sont exécutées à l'aide de lambdas individuels pour les instances de base de données et les clusters de base de données. respectivement.
Pour suivre l'achèvement/l'échec de chaque opération, les serveurs RDS sont utilisés avec des délais et un nombre maximal de tentatives configurés en fonction du délai d'expiration lambda. Pour les scénarios de disponibilité et de suppression de cluster de bases de données, des serveurs personnalisés ont été définis.
Les couches Lambda sont utilisées dans tous les lambdas pour les méthodes utilitaires courantes et la gestion personnalisée des exceptions.

Sur la base des commentaires fournis au**DBRestoreStateMachine**fonction step, les étapes/branches suivantes sont exécutées :

1.  En utilisant le`isCluster`valeur, un branchement a lieu dans la machine à états pour exécuter le pipeline pour un cluster de base de données ou pour une instance de base de données.

2.  Si`task`est réglé sur`create_snapshot`, le**création/mise à jour d'instantanés**Le processus a lieu respectivement pour un cluster ou une instance.
    Crée un instantané à l'aide de l'identifiant unique :_identifier_-instantané, s'il n'existe pas. Si un instantané existe déjà avec l'identifiant susmentionné, il est supprimé et un nouvel instantané est créé. Publiez la nouvelle création d'instantané, le pipeline de restauration de base de données s'exécute.

3.  Si`task`est réglé sur`db_restore`, le processus de restauration de la base de données démarre, sans création/mise à jour d'instantané

4.  Si`task`est réglé sur`create_snapshot_only`, le**création/mise à jour d'instantanés**le processus n’a lieu que pour un cluster ou une instance respectivement.
    Crée un instantané à l'aide de l'identifiant unique :_identifier_-instantané, s'il n'existe pas. Si un instantané existe déjà avec l'identifiant susmentionné, il est supprimé et un nouvel instantané est créé. Dans ce scénario, le pipeline de restauration de base de données n'est pas démarré.

5.  Dans le cadre du processus de restauration de la base de données, la première étape est**Renommer**de l'instance de base de données ou du cluster de base de données fourni et de ses instances correspondantes à un nom temporaire.
    Attendez la réussite de l'étape de renommage pour pouvoir utiliser le nom unique fourni.`identifier`dans l'étape de restauration.

6.  Une fois l'étape de renommage terminée, l'étape suivante consiste à**Restaurer**l'instance de base de données ou le cluster de base de données à l'aide du`identifier`paramètre et l'identifiant de l'instantané comme_identifier_-instantané

7.  Une fois la restauration terminée et l'instance de base de données ou le cluster de base de données disponible, la dernière étape consiste à**Supprimer**l'instance ou le cluster initialement renommé (ainsi que ses instances) qui a été conservé à des fins de gestion des échecs.
    Exécuté à l'aide de lambdas créés à des fins de suppression, une fois la suppression réussie, le pipeline est terminé.

8.  À chaque étape, les tentatives avec alertes d'interruption et d'échec sont traitées à chaque étape de la machine à états. En cas de panne, une alerte par e-mail SES est envoyée comme configuré lors de la configuration. En option, si`SlackWebhookUrls`a été fourni dans le[installation](#slack-setup), les notifications d'échec seront également envoyées aux canaux appropriés.

9.  Si l'étape de restauration échoue, dans le cadre de la gestion des échecs, le**Étape 4**Le changement de nom de l'instance/du cluster est inversé pour garantir que l'instance de base de données ou le cluster de base de données d'origine est disponible pour utilisation.

![DBRestore failure handling depiction](screenshots/failure_handling.png)

**Article du blog Amazon**:<https://aws.amazon.com/blogs/opensource/what-is-trapheus/>

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#contributing-to-trapheus)

## Contribuer à Trapheus

Structure du code de référence

```bash

├── LICENSE.md                                        <-- The MIT license.
├── README.md                                         <-- The Readme file.
├── docs                                              <-- The Readme files
│   ├── README.fr.md
│   └── README.zh-CN.md
├── install.py
├── labs
├── presentation
│   └── Trapheus.pptx
├── requirements.txt
├── screenshots                                       <-- Folder for screenshots of the state machine.
│   ├── Trapheus.gif
│   ├── Trapheus.png
│   ├── cluster_restore.png
│   ├── cluster_snapshot_branch.png
│   ├── failure_handling.png
│   ├── instance_restore.png
│   ├── instance_snapshot_branch.png
│   ├── isCluster_branching.png
│   └── restore_state_machine.png
├── setup.py
├── src
│   ├── checkstatus
│   │   ├── DBClusterStatusWaiter.py                  <-- Python Waiter(https://boto3.amazonaws.com/v1/documentation/api/latest/guide/clients.html#waiters) for checking the status of the cluster
│   │   ├── get_dbcluster_status_function.py          <-- Python Lambda code for polling the status of a clusterised database
│   │   ├── get_dbstatus_function.py                  <-- Python Lambda code for polling the status of a non clusterised RDS instance
│   │   └── waiter_acceptor_config.py                 <-- Config module for the waiters
│   ├── common                                        <-- Common modules across the state machine deployed as a AWS Lambda layer.
│   │   ├── common.zip
│   │   └── python
│   │       ├── constants.py                          <-- Common constants used across the state machine.
│   │       ├── custom_exceptions.py                  <-- Custom exceptions defined for the entire state machine.
│   │       └── utility.py                            <-- Utility module.
│   ├── delete
│   │   ├── cluster_delete_function.py                <-- Python Lambda code for deleting a clusterised database.
│   │   └── delete_function.py                        <-- Python Lambda code for deleting a non clusterised RDS instance.
│   ├── emailalert
│   │   └── email_function.py                         <-- Python Lambda code for sending out failure emails.
│   ├── export
│   │   ├── export_cluster_snapshot_s3_function.py    <-- Python Lambda code for exporting db cluster snapshot to S3.
│   │   └── export_snapshot_s3_function.py            <-- Python Lambda code for exporting db instance snapshot to S3.
│   ├── rename
│   │   ├── cluster_rename_function.py                <-- Python Lambda code for renaming a clusterised database.
│   │   └── rename_function.py                        <-- Python Lambda code for renaming a non-clusterised RDS instance.
│   ├── restore
│   │   ├── cluster_restore_function.py               <-- Python Lambda code for retoring a clusterised database.
│   │   └── restore_function.py                       <-- Python Lambda code for restoring a non-clusterised RDS instance
│   ├── slackNotification
│   │   └── slack_notification.py                     <-- Python Lambda code for sending out a failure alert to configured webhook(s) on Slack.
│   └── snapshot
│       ├── cluster_snapshot_function.py              <-- Python Lambda code for creating a snapshot of a clusterised database.
│       └── snapshot_function.py                      <-- Python Lambda code for creating a snapshot of a non-clusterised RDS instance.
├── template.yaml                                     <-- SAM template definition for the entire state machine.
└── tests
    └── unit
        ├── checkstatus
        │   ├── test_get_dbcluster_status_function.py
        │   └── test_get_dbstatus_function.py
        ├── delete
        │   ├── test_cluster_delete_function.py
        │   └── test_delete_function.py
        ├── emailalert
        │   └── test_email_function.py
        ├── export
        │   ├── test_export_cluster_snapshot_s3_function.py
        │   └── test_export_snapshot_s3_function.py
        ├── rename
        │   ├── test_cluster_rename_function.py
        │   └── test_rename_function.py
        ├── restore
        │   ├── test_cluster_restore_function.py
        │   └── test_restore_function.py
        ├── slackNotification
        │   └── test_slack_notification.py
        └── snapshot
            ├── test_cluster_snapshot_function.py
            └── test_snapshot_function.py

```

Préparez votre environnement. Installez les outils selon vos besoins.

-   [Git-Bash](https://gitforwindows.org/)utilisé pour exécuter Git à partir de la ligne de commande.
-   [Bureau Github](https://desktop.github.com/)Outil de bureau Git pour gérer les demandes d'extraction, les branches et les dépôts.
-   [Code de Visual Studio](https://code.visualstudio.com/)Éditeur visuel complet. Des extensions pour GitHub peuvent être ajoutées.
-   Ou un éditeur de votre choix.

1.  Dépôt Fork Trapheus

2.  Créez une branche fonctionnelle.
    ```bash
    git branch trapheus-change1
    ```

3.  Confirmez la branche active pour les modifications.
    ```bash
     git checkout trapheus-change1
    ```
    Vous pouvez combiner les deux commandes en tapant`git checkout -b trapheus-change1`.

4.  Apportez des modifications localement à l'aide d'un éditeur et ajoutez des tests unitaires si nécessaire.

5.  Exécutez la suite de tests dans le référentiel pour vous assurer que les flux existants ne sont pas interrompus.
    ```bash
       cd Trapheus
       python -m pytest tests/ -v #to execute the complete test suite
       python -m pytest tests/unit/test_get_dbstatus_function.py -v #to execute any individual test
    ```

6.  Mettre en scène les fichiers édités.
    ```bash
       git add contentfile.md 
    ```
    Ou utiliser`git add . `pour plusieurs fichiers.

7.  Validez les modifications à partir de la préparation.
    ```bash
       git commit -m "trapheus-change1"
    ```

8.  Appliquer de nouvelles modifications à GitHub
    ```bash
       git push --set-upstream origin trapheus-change1
    ```

9.  Vérifier le statut de la succursale
    ```bash
    git status
    ```
    Revoir`Output`pour confirmer le statut de validation.


1.  Git pousser
    ```bash
        git push --set-upstream origin trapheus-change1
    ```

2.  Le`Output`fournira un lien pour créer votre Pull Request.

## Contributeurs

<a href="https://github.com/intuit/Trapheus/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=intuit/Trapheus" />
</a>
