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

-   **Important:**cette application utilise divers services AWS et il y a des coûts associés à ces services après l'utilisation de l'offre gratuite - veuillez consulter le[Page de tarification AWS](https://aws.amazon.com/pricing/)pour plus de détails.

<details>
<summary>📖 Table of Contents</summary>
<br />

[![\---------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#table-of-contents)

## ➤ Table des matières

-   -   [➤ Prérequis](#-pre-requisites)
-   -   [➤ Paramètres](#-parameters)
-   -   [➤ Mode d'emploi](#-instructions)
-   -   [➤ Exécution](#-execution)
-   -   [➤ Comment ça marche](#-how-it-works)
-   -   [➤ Contribuer à Trapheus](#-contributing-to-trapheus)
-   -   [➤ Contributeurs](#-contributors)
-   -   [➤ Montrez votre soutien](#-show-your-support)

</details>

[![\---------------------------------------------------------------------------------------------------------------------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#pre-requisites)

## ➤ Prérequis

L'application nécessite que les ressources AWS suivantes existent avant l'installation :

1.  `python3.7`installé sur la machine locale suivant[ce](https://www.python.org/downloads/).

2.  Configurer[AWS SES](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/event-publishing-create-configuration-set.html)
    -   Configurez l'e-mail de l'expéditeur et du destinataire SES ([SES Console](https://console.aws.amazon.com/ses/)-> Adresses e-mail).
        -   Une alerte par e-mail SES est configurée pour informer l'utilisateur de toute défaillance de la machine d'état. Le paramètre de l'e-mail de l'expéditeur est nécessaire pour configurer l'ID d'e-mail via lequel l'alerte est envoyée. Le paramètre d'e-mail du destinataire est nécessaire pour définir l'ID d'e-mail auquel l'alerte est envoyée.

3.  Créez le bucket S3 dans lequel le système va stocker les modèles de formation de nuages :
    -   Nom proposé : trapheus-cfn-s3-[identifiant de compte-]-[région]. Il est recommandé que le nom contienne votre :
        -   account-id, car les noms de compartiment doivent être globaux (empêche quelqu'un d'autre d'avoir le même nom)
        -   région, pour garder facilement une trace lorsque vous avez des buckets trapheus-s3 dans plusieurs régions

4.  Un VPC (spécifique à une région). Le même VPC/région doit être utilisé à la fois pour la ou les instances RDS, à utiliser dans Trapheus, et pour les lambdas de Trapheus.
    -   Considération de la sélection de la région. Régions prenant en charge :
        -   [Réception d'e-mails](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/regions.html#region-receive-email). Vérifier[Paramètres](#parameters)-> 'RecipientEmail' pour en savoir plus.
    -   Exemple de configuration VPC minimale :
        -   Console VPC :
            -   nom : Trapheus-VPC-[région]\(spécifie le[région]où votre VPC est créé - pour garder facilement une trace lorsque vous avez des VPC Trapheus dans plusieurs régions)
            -   [Bloc CIDR IPv4](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html#vpc-sizing-ipv4): 10.0.0.0/16
        -   Console VPC->Page Sous-réseaux et créez deux sous-réseaux privés :
            -   Sous-réseau 1 :
                -   VPC : VPC Trapheus[région]
                -   Zone de disponibilité : choisissez-en une
                -   Bloc CIDR IPv4 : 10.0.0.0/19
            -   Sous-réseau2 :
                -   VPC : VPC Trapheus[région]
                -   Zone de disponibilité : choisissez-en une différente de celle de Subnet1 AZ.
                -   Bloc CIDR IPv4 : 10.0.32.0/19
        -   Vous avez créé un VPC avec seulement deux sous-réseaux privés. Si vous créez des sous-réseaux non privés, vérifiez[le rapport entre les sous-réseaux privés et publics, le sous-réseau privé avec ACL de réseau personnalisé dédié et la capacité de réserve](https://docs.aws.amazon.com/quickstart/latest/vpc/architecture.html).

5.  Une ou plusieurs instances d'une base de données RDS que vous souhaitez restaurer.
    -   Exemple minimal_gratuit_Configuration RDS :
        -   Options de moteur : MySQL
        -   Modèles : version gratuite
        -   Paramètres : entrez le mot de passe
        -   Connectivité : VPC : Trapheus VPC[région]

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#parameters)

## ➤ Paramètres

Voici les paramètres de création du modèle cloudformation :

1.  `--s3-bucket`:[Facultatif]Le nom du compartiment S3 du modèle CloudFormation à partir du[Conditions préalables](#pre-requisites).
2.  `vpcID`:[Requis]L'ID du VPC du[Conditions préalables](#pre-requisites). Les lambdas de la machine d'état Trapheus seront créés dans ce VPC.
3.  `Subnets`:[Requis]Une liste séparée par des virgules d'ID de sous-réseau privé (spécifique à la région) du[Conditions préalables](#pre-requisites)VPC.
4.  `SenderEmail`:[Requis]L'e-mail d'envoi SES configuré dans le[Conditions préalables](#pre-requisites)
5.  `RecipientEmail`:[Requis]Liste séparée par des virgules des adresses e-mail des destinataires configurées dans[Conditions préalables](#pre-requisites).
6.  `UseVPCAndSubnets`:[Facultatif]S'il faut utiliser le vpc et les sous-réseaux pour créer un groupe de sécurité et lier le groupe de sécurité et le vpc aux lambdas. Lorsque UseVPCAndSubnets est omis (par défaut) ou défini sur "true", les lambdas sont connectés à un VPC dans votre compte et, par défaut, la fonction ne peut pas accéder au RDS (ou à d'autres services) si le VPC ne fournit pas l'accès (soit par acheminer le trafic sortant vers un[passerelle NAT](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html)dans un sous-réseau public, ou ayant un[Point de terminaison d'un VPC](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-endpoints.html), qui entraînent tous deux des coûts ou nécessitent plus de configuration). S'il est défini sur 'false', le[les lambdas s'exécuteront dans un VPC appartenant à Lambda par défaut qui a accès à RDS (et à d'autres services AWS)](https://docs.aws.amazon.com/lambda/latest/dg/configuration-vpc.html#vpc-internet).
7.  `SlackWebhookUrls`:[Facultatif]Liste séparée par des virgules des webhooks Slack pour les alertes d'échec.

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#instructions)

## ➤ Mode d'emploi

### Installation

#### Pour configurer le Trapheus dans votre compte AWS, suivez les étapes ci-dessous :

1.  Cloner le dépôt Trapheus Git
2.  Configuration des informations d'identification AWS. Trapheus utilise boto3 comme bibliothèque client pour communiquer avec Amazon Web Services. Ne hésitez pas à[utiliser n'importe quelle variable d'environnement](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html#environment-variables)que boto3 prend en charge pour fournir les identifiants d'authentification.
3.  Courir`pip install -r requirements.txt`pour installer le graphe de dépendance
4.  Courir`python install.py`

<p align="center"><img src="screenshots/Trapheus.gif?raw=true"/></p>

> Toujours confronté à un problème ? Vérifier la[Problèmes](https://github.com/intuit/Trapheus/issues)section ou ouvrir un nouveau sujet

Ce qui précède configurera un CFT dans votre compte AWS avec le nom fourni lors de l'installation.

**A NOTER**:
Le CFT crée les ressources suivantes :

1.  **DBRestoreStateMachineDBRestoreStateMachine**Machine d'état de fonction d'étape
2.  Plusieurs lambdas pour exécuter différentes étapes dans la machine d'état
3.  LambdaExecutionRole : utilisé sur tous les lambdas pour effectuer plusieurs tâches sur RDS
4.  StatesExecutionRole : rôle IAM avec des autorisations pour exécuter la machine d'état et appeler des lambdas
5.  Compartiment S3 : rds-snapshots-&lt;your_account_id> vers lequel les instantanés seront exportés
6.  Clé KMS : nécessaire pour démarrer la tâche d'exportation de l'instantané vers s3
7.  DBRestoreStateMachineEventRule : une règle Cloudwatch à l'état désactivé, qui peut être utilisée ci-dessus[instructions](#to-set-up-the-step-function-execution-through-a-scheduled-run-using-cloudwatch-rule-follow-the-steps-below)basé sur l'exigence de l'utilisateur
8.  CWEventStatesExecutionRole : rôle IAM utilisé par la règle DBRestoreStateMachineEventRule CloudWatch, pour autoriser l'exécution de la machine d'état à partir de CloudWatch

#### Pour configurer l'exécution de la fonction d'étape via une exécution planifiée à l'aide de la règle CloudWatch, suivez les étapes ci-dessous :

1.  Accédez à la section DBRestoreStateMachineEventRule dans le template.yaml du référentiel Trapheus.
2.  Nous l'avons défini comme une règle cron planifiée pour s'exécuter tous les VENDREDIS à 8h00 UTC. Vous pouvez le changer à votre fréquence de planification préférée en mettant à jour le**ScheduleExpression**la valeur de la propriété en conséquence. Exemples:

    -   Pour l'exécuter tous les 7 jours,`ScheduleExpression: "rate(7 days)"`
    -   Pour l'exécuter tous les VENDREDIS à 8h00 UTC,`ScheduleExpression: "cron(0 8 ? * FRI *)"`

    Cliquez sur[ici](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)pour tous les détails sur la façon de définir ScheduleExpression.
3.  Exemples d'objectifs donnés dans le fichier modèle sous**Cibles**propriété pour votre référence doit être mise à jour :

    un. Changement**Saisir**propriété en fonction de vos valeurs de propriété d'entrée, donnez en conséquence un meilleur ID pour votre cible en mettant à jour le**Identifiant**propriété.

    b. En fonction du nombre de cibles pour lesquelles vous souhaitez définir la planification, ajoutez ou supprimez les cibles.
4.  Changer la**État**valeur de la propriété à**ACTIVÉ**
5.  Enfin, empaquetez et redéployez la pile en suivant les étapes 2 et 3 dans[Configuration trapèze](#to-setup-the-trapheus-in-your-aws-account-follow-the-steps-below)

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#execution)

## ➤ Exécution

Pour exécuter la fonction pas à pas, suivez les étapes ci-dessous :

1.  Accédez à la définition de la machine d'état à partir du_Ressources_onglet dans la pile cloudformation.
2.  Cliquer sur_Démarrer l'exécution_.
3.  Sous_Saisir_, indiquez le json suivant en tant que paramètre :


    {
        "identifier": "<identifier name>",
        "task": "<taskname>",
        "isCluster": true or false
    }

un.`identifier`: (Obligatoire - Chaîne) L'identificateur d'instance ou de cluster RDS qui doit être restauré. Tout type d'instance RDS ou de clusters Amazon Aurora est pris en charge.

b.`task`: (Obligatoire - Chaîne) Les options valides sont`create_snapshot`ou`db_restore`ou`create_snapshot_only`.

c.`isCluster`: (Obligatoire - Booléen) Défini sur`true`si l'identifiant fourni est celui d'un cluster, sinon défini sur`false`

La machine d'état peut effectuer l'une des tâches suivantes :

1.  si`task`est réglé sur`create_snapshot`, la machine d'état crée/met à jour un instantané pour l'instance ou le cluster RDS donné à l'aide de l'identifiant d'instantané :_identifier_-instantané puis exécute le pipeline
2.  si`task`est réglé sur`db_restore`, la machine d'état effectue une restauration sur l'instance RDS donnée, sans mettre à jour un instantané, en supposant qu'il existe un instantané existant avec un identifiant :_identifier_-instantané
3.  si`task`est réglé sur`create_snapshot_only`, la machine d'état crée/met à jour un instantané pour l'instance ou le cluster RDS donné à l'aide de l'identifiant d'instantané :_identifier_-snapshot et il n'exécuterait pas le pipeline

**Considérations de coût**

Après avoir terminé avec le développement ou l'utilisation de l'outil :

1.  si vous n'avez pas besoin de l'instance RDS lorsque vous ne codez pas ou n'utilisez pas l'outil (par exemple, s'il s'agit d'un test RDS), envisagez d'arrêter ou de supprimer la base de données. Vous pouvez toujours le recréer quand vous en avez besoin.
2.  si vous n'avez pas besoin des anciens modèles Cloud Formation, il est recommandé de vider le compartiment CFN S3.

**Démolir**

Pour démonter votre application et supprimer toutes les ressources associées à la machine d'état de Trapheus DB Restore, suivez ces étapes :

1.  Connectez-vous au[Console Amazon CloudFormation](https://console.aws.amazon.com/cloudformation/home?#)et trouvez la pile que vous avez créée.
2.  Supprimez la pile. Notez que la suppression de la pile échouera si le compartiment rds-snapshots-&lt;YOUR_ACCOUNT_NO> s3 n'est pas vide. Supprimez donc d'abord les exportations des instantanés dans le compartiment.
3.  Supprimez les ressources AWS du[Conditions préalables](#pre-requisites). La suppression de SES, du bucket CFN S3 (videz-le s'il n'est pas supprimé) et du VPC est facultative car vous ne verrez pas les frais, mais vous pourrez les réutiliser plus tard pour un démarrage rapide.

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#how-it-works)

## ➤ Comment ça marche

**Canalisation complète**

![DBRestore depiction](screenshots/restore_state_machine.png)

Modélisé comme une machine d'état, différentes étapes du flux telles que la création/mise à jour d'instantanés, le changement de nom d'instance, la restauration et la suppression, l'état d'achèvement/d'échec de chaque opération, l'alerte par e-mail d'échec, etc. sont exécutées à l'aide de lambdas individuels pour les instances de base de données et les clusters de base de données respectivement.
Pour suivre l'achèvement/l'échec de chaque opération, les serveurs RDS sont utilisés avec des retards et un nombre maximal de tentatives configurées en fonction du délai d'attente lambda. Pour les scénarios de disponibilité et de suppression du cluster de bases de données, des serveurs personnalisés ont été définis.
Les couches lambda sont utilisées dans tous les lambdas pour les méthodes utilitaires courantes et la gestion personnalisée des exceptions.

Sur la base des informations fournies au**DBRestoreStateMachineDBRestoreStateMachine**fonction step, les étapes/branches suivantes sont exécutées :

1.  En utilisant le`isCluster`valeur, un branchement a lieu dans la machine d'état pour exécuter le pipeline pour un cluster de base de données ou pour une instance de base de données.

2.  Si`task`est réglé sur`create_snapshot`, le**création/mise à jour d'instantanés**processus a lieu pour un cluster ou une instance respectivement.
    Crée un instantané à l'aide de l'identifiant unique :_identifier_-instantané, s'il n'existe pas. Si un instantané existe déjà avec l'identifiant susmentionné, il est supprimé et un nouvel instantané est créé.

3.  Si`task`est réglé sur`db_restore`, le processus de restauration de la base de données démarre, sans création/mise à jour d'instantané

4.  Si`task`est réglé sur`create_snapshot_only`, le**création/mise à jour d'instantanés**le processus n'a lieu que pour un cluster ou une instance respectivement.
    Crée un instantané à l'aide de l'identifiant unique :_identifier_-instantané, s'il n'existe pas. Si un instantané existe déjà avec l'identifiant susmentionné, il est supprimé et un nouvel instantané est créé.

5.  Dans le cadre du processus de restauration de la base de données, la première étape consiste à**Renommer**de l'instance de base de données ou du cluster de base de données fourni et de ses instances correspondantes à un nom temporaire.
    Attendez la réussite de l'étape de renommage pour pouvoir utiliser l'unique`identifier`dans l'étape de restauration.

6.  Une fois l'étape de renommage terminée, l'étape suivante consiste à**Restaurer**l'instance de base de données ou le cluster de base de données à l'aide de`identifier`paramètre et l'identifiant de l'instantané comme_identifier_-instantané

7.  Une fois la restauration terminée et l'instance de base de données ou le cluster de base de données disponible, la dernière étape consiste à**Supprimer**l'instance ou le cluster initialement renommé (ainsi que ses instances) qui a été conservé à des fins de gestion des pannes.
    Exécuté à l'aide de lambdas créés à des fins de suppression, une fois la suppression réussie, le pipeline est terminé.

8.  À chaque étape, les nouvelles tentatives avec interruption et alertes d'échec sont gérées à chaque étape de la machine d'état. En cas de défaillance, une alerte par e-mail SES est envoyée comme configuré lors de la configuration. Facultativement, si`SlackWebhookUrls`a été fourni dans le[installation](#slack-setup), les notifications d'échec seront également envoyées aux canaux appropriés.

9.  Si l'étape de restauration échoue, dans le cadre de la gestion des échecs, le**Étape 4**du renommage de l'instance/du cluster est annulé pour garantir que l'instance de base de données ou le cluster de base de données d'origine est disponible à l'utilisation.

![DBRestore failure handling depiction](screenshots/failure_handling.png)

[![\-----------------------------------------------------](https://raw.githubusercontent.com/andreasbm/readme/master/assets/lines/colored.png)](#contributing-to-trapheus)

## ➤ Contribuer à Trapheus

Structure du code de référence

```bash

├── CONTRIBUTING.md                               <-- How to contribute to Trapheus
├── LICENSE.md                                    <-- The MIT license.
├── README.md                                     <-- The Readme file.
├── events
│   └── event.json                                <-- JSON event file to be used for local SAM testing
├── screenshots                                   <-- Folder for screenshots of teh state machine.
│   ├── Trapheus-logo.png
│   ├── cluster_restore.png
│   ├── cluster_snapshot_branch.png
│   ├── failure_handling.png
│   ├── instance_restore.png
│   ├── instance_snapshot_branch.png
│   ├── isCluster_branching.png
│   └── restore_state_machine.png
├── src
│   ├── checkstatus
│   │   ├── DBClusterStatusWaiter.py              <-- Python Waiter(https://boto3.amazonaws.com/v1/documentation/api/latest/guide/clients.html#waiters) for checking the status of the cluster
│   │   ├── get_dbcluster_status_function.py      <-- Python Lambda code for polling the status of a clusterised database
│   │   ├── get_dbstatus_function.py              <-- Python Lambda code for polling the status of a non clusterised RDS instance
│   │   └── waiter_acceptor_config.py             <-- Config module for the waiters
│   ├── common                                    <-- Common modules across the state machine deployed as a AWS Lambda layer.
│   │   ├── common.zip
│   │   └── python
│   │       ├── constants.py                      <-- Common constants used across the state machine.
│   │       ├── custom_exceptions.py              <-- Custom exceptions defined for the entire state machine.
│   │       └── utility.py                        <-- Utility module.
│   ├── delete
│   │   ├── cluster_delete_function.py           <-- Python Lambda code for deleting a clusterised database.
│   │   └── delete_function.py                   <-- Python Lambda code for deleting a non clusterised RDS instance.
│   ├── emailalert
│   │   └── email_function.py                    <-- Python Lambda code for sending out failure emails.
│   ├── rename
│   │   ├── cluster_rename_function.py           <-- Python Lambda code for renaming a clusterised database.
│   │   └── rename_function.py                   <-- Python Lambda code for renaming a non-clusterised RDS instance.
│   ├── restore
│   │   ├── cluster_restore_function.py          <-- Python Lambda code for retoring a clusterised database.
│   │   └── restore_function.py                  <-- Python Lambda code for restoring a non-clusterised RDS instance
│   ├── slackNotification
│   │   └── slack_notification.py                <-- Python Lambda code for sending out a failure alert to configured webhook(s) on Slack.
│   └── snapshot
│       ├── cluster_snapshot_function.py         <-- Python Lambda code for creating a snapshot of a clusterised database.
│       └── snapshot_function.py                 <-- Python Lambda code for creating a snapshot of a non-clusterised RDS instance.
├── template.yaml                                <-- SAM template definition for the entire state machine.
└── tests                                        <-- Test folder.
    └── unit
        ├── mock_constants.py
        ├── mock_custom_exceptions.py
        ├── mock_import.py
        ├── mock_utility.py
        ├── test_cluster_delete_function.py
        ├── test_cluster_rename_function.py
        ├── test_cluster_restore_function.py
        ├── test_cluster_snapshot_function.py
        ├── test_delete_function.py
        ├── test_email_function.py
        ├── test_get_dbcluster_status_function.py
        ├── test_get_dbstatus_function.py
        ├── test_rename_function.py
        ├── test_restore_function.py
        ├── test_slack_notification.py
        └── test_snapshot_function.py

```

Préparez votre environnement. Installez les outils au besoin.

-   [Coup de git](https://gitforwindows.org/)utilisé pour exécuter Git à partir de la ligne de commande.
-   [Bureau Github](https://desktop.github.com/)Outil de bureau Git pour gérer les pull requests, les branches et les dépôts.
-   [Code Visual Studio](https://code.visualstudio.com/)Éditeur visuel complet. Des extensions pour GitHub peuvent être ajoutées.
-   Ou un éditeur de votre choix.

1.  Fourche Trapheus repo

2.  Créez une branche de travail.
    ```bash
    git branch trapheus-change1
    ```

3.  Confirmez la branche de travail pour les modifications.
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

7.  Validez les modifications à partir de la mise en scène.
    ```bash
       git commit -m "trapheus-change1"
    ```

8.  Pousser de nouvelles modifications vers GitHub
    ```bash
       git push --set-upstream origin trapheus-change1
    ```

9.  Vérifier le statut de la succursale
    ```bash
    git status
    ```
    Revoir`Output`pour confirmer l'état de validation.


1.  Poussée de git
    ```bash
        git push --set-upstream origin trapheus-change1
    ```

2.  Le`Output`fournira un lien pour créer votre demande d'extraction.

## ➤ Contributeurs

<a href="https://github.com/intuit/Trapheus/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=intuit/Trapheus" />
</a>
