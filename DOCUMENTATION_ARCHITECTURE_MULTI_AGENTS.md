# Documentation de l'Architecture Multi-Agents et Système de Recherche de Standards avec Versioning

## Table des Matières

1. [Vue d'ensemble du Système](#vue-densemble-du-système)
2. [Architecture Multi-Agents](#architecture-multi-agents)
3. [Agents Spécialisés](#agents-spécialisés)
4. [Système de Recherche Web de Standards](#système-de-recherche-web-de-standards)
5. [Système de Versioning](#système-de-versioning)
6. [Pipelines d'Orchestration](#pipelines-dorchestration)
7. [Diagrammes UML](#diagrammes-uml)
8. [Flux de Données](#flux-de-données)

## Vue d'ensemble du Système

Le système GRC (Gouvernance, Risque et Conformité) Assistant est une plateforme sophistiquée utilisant une architecture multi-agents pour l'évaluation des politiques de sécurité et l'analyse des cas d'usage dans le secteur bancaire et financier.

### Architecture Globale

```mermaid
graph TB
    subgraph "Interface Utilisateur"
        UI[Interface Web React/Next.js]
        API[API FastAPI]
    end
    
    subgraph "Couche Multi-Agents"
        PA[Agents d'Évaluation de Politiques]
        UA[Agents d'Analyse de Cas d'Usage]
        KPI[Agent KPI]
        BA[Agent de Base]
    end
    
    subgraph "Orchestration"
        PEP[Pipeline d'Évaluation de Politiques]
        UCP[Pipeline de Traitement de Cas d'Usage]
    end
    
    subgraph "Système de Standards"
        SST[Traceur de Standards de Sécurité]
        VM[Gestionnaire de Versions]
        WF[Récupérateur Web]
    end
    
    subgraph "Stockage de Données"
        VDB[Base de Données Vectorielle]
        FS[Système de Fichiers]
        IDX[Index Llama]
    end
    
    UI --> API
    API --> PA
    API --> UA
    PA --> PEP
    UA --> UCP
    PEP --> BA
    UCP --> KPI
    SST --> VM
    SST --> WF
    VM --> VDB
    VDB --> IDX
    WF --> FS
```

## Architecture Multi-Agents

### Hiérarchie des Agents

```mermaid
classDiagram
    class Agent {
        +system_prompt: str
        +memory: List
        +tools: List
        +llm: ChatGoogleGenerativeAI
        +invoke_with_retry()
        +add_to_memory()
        +generate_response()
    }
    
    class GapCheckerAgent {
        +analyze_gaps()
        +GapAnalysisOutput
    }
    
    class ComplianceCheckerAgent {
        +check_compliance()
        +ComplianceAssessmentOutput
    }
    
    class PolicyEnhancerAgent {
        +enhance_policy()
        +PolicyEnhancementOutput
    }
    
    class KPIAgent {
        +calculate_kpis()
        +KPIAnalysisOutput
    }
    
    class DeploymentAnalyzerAgent {
        +analyze_deployment()
        +DeploymentAnalysisOutput
    }
    
    class UseCaseJudgeAgent {
        +judge_use_case()
        +UseCaseJudgmentOutput
    }
    
    Agent <|-- GapCheckerAgent
    Agent <|-- ComplianceCheckerAgent
    Agent <|-- PolicyEnhancerAgent
    Agent <|-- KPIAgent
    Agent <|-- DeploymentAnalyzerAgent
    Agent <|-- UseCaseJudgeAgent
```

## Agents Spécialisés

### 1. Agents d'Évaluation de Politiques

#### Agent de Vérification des Lacunes (GapCheckerAgent)
- **Objectif** : Identifier les éléments manquants dans les politiques de sécurité par rapport aux standards
- **Spécialisation** : Analyse comparative détaillée entre politiques et standards de référence
- **Sortie structurée** : Classification (GOOD/MISSING/NON_COMPLIANT), lacunes identifiées, justification

#### Agent de Vérification de Conformité (ComplianceCheckerAgent)
- **Objectif** : Évaluer le niveau de conformité des politiques aux standards de sécurité
- **Spécialisation** : Analyse de conformité réglementaire (PCI-DSS, SOX, Basel III)
- **Sortie structurée** : Score de conformité, problèmes identifiés, recommandations

#### Agent d'Amélioration de Politiques (PolicyEnhancerAgent)
- **Objectif** : Proposer des améliorations concrètes pour les politiques existantes
- **Spécialisation** : Génération de contenu amélioré basé sur les meilleures pratiques
- **Sortie structurée** : Contenu amélioré, changements apportés, justification

### 2. Agents d'Analyse de Cas d'Usage

#### Agent KPI (KPIAgent)
- **Objectif** : Calculer et analyser les indicateurs de performance de sécurité
- **Spécialisation** : Métriques bancaires et financières spécialisées
- **KPIs analysés** :
  - Efficacité de gestion des vulnérabilités
  - Temps moyen de détection (MTTD) et de réponse (MTTR)
  - Taux de détection d'anomalies transactionnelles
  - Score de sécurité des transactions
  - Disponibilité système (99,9%+ requis)
  - Efficacité de détection de fraude

```mermaid
graph LR
    subgraph "KPIs de Sécurité Bancaire"
        VME[Efficacité Gestion Vulnérabilités]
        MTTD[Temps Moyen de Détection]
        MTTR[Temps Moyen de Réponse]
        TAD[Taux Détection Anomalies]
        TSI[Index Sécurité Transactions]
        SA[Disponibilité Système]
        FDE[Efficacité Détection Fraude]
        ESS[Score Force Chiffrement]
    end
    
    VME --> OS[Score Global]
    MTTD --> OS
    MTTR --> OS
    TAD --> OS
    TSI --> OS
    SA --> OS
    FDE --> OS
    ESS --> OS
```

#### Agent d'Analyse de Déploiement (DeploymentAnalyzerAgent)
- **Objectif** : Évaluer la faisabilité et les aspects d'implémentation des cas d'usage
- **Spécialisation** : Considérations spécifiques au secteur bancaire
- **Analyse** :
  - Score de faisabilité (0-100)
  - Exigences réglementaires bancaires
  - Intégration avec systèmes bancaires centraux
  - Estimation temporelle et ressources nécessaires
  - Facteurs de risque et stratégies de mitigation

#### Agent de Jugement de Cas d'Usage (UseCaseJudgeAgent)
- **Objectif** : Évaluer la qualité et l'efficacité des cas d'usage de sécurité
- **Spécialisation** : Alignement avec standards et politiques de sécurité
- **Évaluation** :
  - Score d'efficacité
  - Alignement avec standards et politiques
  - Impact sécuritaire global
  - Lacunes identifiées et suggestions d'amélioration

## Système de Recherche Web de Standards

### Architecture du Traceur de Standards

```mermaid
graph TB
    subgraph "Système de Traceur de Standards de Sécurité"
        SST[SecurityStandardsTracker]
        VM[StandardsVersionManager]
        WF[SecurityNewsFetcher]
        VDB[Base de Données Vectorielle]
    end
    
    subgraph "Sources Web"
        NIST[NIST Cybersecurity Framework]
        ISO[ISO 27001/27002]
        PCIDSS[PCI-DSS]
        SOX[Sarbanes-Oxley]
        BASEL[Basel III]
        GDPR[RGPD]
    end
    
    subgraph "Stockage"
        VS[Versions de Standards]
        CS[Changements de Standards]
        IDX[Index Vectoriel]
    end
    
    WF --> NIST
    WF --> ISO
    WF --> PCIDSS
    WF --> SOX
    WF --> BASEL
    WF --> GDPR
    
    SST --> VM
    SST --> WF
    SST --> VDB
    
    VM --> VS
    VM --> CS
    VDB --> IDX
```

### Processus de Récupération Web

```mermaid
sequenceDiagram
    participant CLI as Interface CLI
    participant SST as SecurityStandardsTracker
    participant WF as SecurityNewsFetcher
    participant VM as VersionManager
    participant VDB as VectorDB
    
    CLI->>SST: check_for_updates()
    SST->>WF: fetch_security_news()
    WF->>WF: search_strategy_1()
    WF->>WF: search_strategy_2()
    WF->>WF: search_strategy_3()
    WF-->>SST: news_items[]
    
    SST->>VM: process_updates()
    VM->>VM: compare_with_existing()
    VM->>VM: calculate_similarity()
    VM->>VM: generate_version_id()
    VM-->>SST: version_info
    
    SST->>VDB: update_embeddings()
    VDB-->>SST: success
    SST-->>CLI: update_report
```

## Système de Versioning

### Gestionnaire de Versions de Standards

Le `StandardsVersionManager` gère les différentes versions des standards de sécurité avec les fonctionnalités suivantes :

#### Fonctionnalités Principales

1. **Ajout de Nouvelles Versions**
   - Génération automatique d'ID de version
   - Métadonnées de version (timestamp, source, description)
   - Calcul de similarité avec versions existantes

2. **Suivi des Changements**
   - Détection automatique des modifications
   - Comparaison sémantique entre versions
   - Génération de rapports de changements

3. **Historique des Versions**
   - Stockage persistant des versions
   - Récupération de l'historique complet
   - Navigation entre versions

```mermaid
erDiagram
    STANDARD {
        string standard_id
        string name
        string description
        datetime created_at
        string source_url
    }
    
    VERSION {
        string version_id
        string standard_id
        string version_number
        datetime version_date
        string content_hash
        json metadata
        text content
    }
    
    CHANGE {
        string change_id
        string from_version_id
        string to_version_id
        float similarity_score
        json change_summary
        datetime detected_at
    }
    
    STANDARD ||--o{ VERSION : "has_versions"
    VERSION ||--o{ CHANGE : "from_version"
    VERSION ||--o{ CHANGE : "to_version"
```

### Algorithme de Détection de Changements

```mermaid
flowchart TD
    A[Nouveau Contenu de Standard] --> B[Extraction du Texte]
    B --> C[Génération d'Embeddings]
    C --> D[Comparaison avec Versions Existantes]
    D --> E{Similarité > Seuil?}
    E -->|Oui| F[Version Similaire Trouvée]
    E -->|Non| G[Nouvelle Version Détectée]
    F --> H[Analyse des Différences]
    G --> I[Création Nouvelle Version]
    H --> J[Génération Rapport de Changements]
    I --> K[Mise à Jour Index Vectoriel]
    J --> K
    K --> L[Notification des Parties Prenantes]
```

## Pipelines d'Orchestration

### Pipeline d'Évaluation de Politiques

```mermaid
graph TD
    A[Politique d'Entrée] --> B[Segmentation en Chunks]
    B --> C[Agent de Vérification des Lacunes]
    B --> D[Agent de Vérification de Conformité]
    B --> E[Agent d'Amélioration de Politiques]
    
    C --> F[Résultats d'Analyse des Lacunes]
    D --> G[Résultats de Conformité]
    E --> H[Recommandations d'Amélioration]
    
    F --> I[Agrégation des Résultats]
    G --> I
    H --> I
    
    I --> J[Rapport d'Évaluation Combiné]
    
    subgraph "Récupération de Standards"
        K[Base de Données Vectorielle]
        L[Standards Pertinents]
        K --> L
        L --> C
        L --> D
        L --> E
    end
```

### Pipeline de Traitement de Cas d'Usage

```mermaid
graph TD
    A[Cas d'Usage d'Entrée] --> B[Agent KPI]
    A --> C[Agent d'Analyse de Déploiement]
    A --> D[Agent de Jugement de Cas d'Usage]
    
    B --> E[Analyse des KPIs de Sécurité]
    C --> F[Analyse de Faisabilité de Déploiement]
    D --> G[Évaluation de Qualité]
    
    E --> H[Agent d'Agrégation d'Analyses]
    F --> H
    G --> H
    
    H --> I[Rapport de Traitement Complet]
    
    subgraph "Contexte de Référence"
        J[Standards de Sécurité]
        K[Politiques Organisationnelles]
        J --> B
        J --> C
        J --> D
        K --> C
        K --> D
    end
```

## Diagrammes UML

### Diagramme de Classes - Système de Versioning

```mermaid
classDiagram
    class SecurityStandardsTracker {
        -version_manager: StandardsVersionManager
        -web_fetcher: SecurityNewsFetcher
        -rag_system: RAGSystem
        +check_for_updates()
        +track_changes()
        +get_latest_standards()
    }
    
    class StandardsVersionManager {
        -versions_path: Path
        -changes_path: Path
        -embed_model: Any
        -similarity_threshold: float
        +add_version()
        +compare_versions()
        +get_version_history()
        +detect_changes()
    }
    
    class SecurityNewsFetcher {
        -search_engines: List
        -queries: List
        +fetch_security_news()
        +search_strategy_1()
        +search_strategy_2()
        +search_strategy_3()
    }
    
    class RAGSystem {
        -embedding_model: str
        -chunk_size: int
        -vector_index: VectorStoreIndex
        +build_index()
        +query()
        +add_documents()
        +update_index()
    }
    
    SecurityStandardsTracker --> StandardsVersionManager
    SecurityStandardsTracker --> SecurityNewsFetcher
    SecurityStandardsTracker --> RAGSystem
```

### Diagramme de Séquence - Évaluation de Politique

```mermaid
sequenceDiagram
    participant User as Utilisateur
    participant API as API FastAPI
    participant PEP as PolicyEvaluationPipeline
    participant GA as GapCheckerAgent
    participant CA as ComplianceCheckerAgent
    participant PA as PolicyEnhancerAgent
    participant VDB as VectorDB
    
    User->>API: Évaluer Politique
    API->>PEP: evaluate_policy()
    PEP->>PEP: chunk_policy()
    
    loop Pour chaque chunk
        PEP->>VDB: Récupérer standards pertinents
        VDB-->>PEP: Standards
        
        par Analyse en parallèle
            PEP->>GA: analyze_gaps()
            GA-->>PEP: Résultats lacunes
        and
            PEP->>CA: check_compliance()
            CA-->>PEP: Résultats conformité
        and
            PEP->>PA: enhance_policy()
            PA-->>PEP: Recommandations
        end
    end
    
    PEP->>PEP: aggregate_results()
    PEP-->>API: Rapport combiné
    API-->>User: Résultats d'évaluation
```

## Flux de Données

### Architecture de Données Globale

```mermaid
graph TB
    subgraph "Sources de Données"
        POL[Politiques DOCX/PDF]
        STD[Standards de Sécurité]
        UC[Cas d'Usage]
        WEB[Sources Web]
    end
    
    subgraph "Traitement de Données"
        DL[Document Loader]
        EM[Embedding Manager]
        CS[Chunking Service]
    end
    
    subgraph "Stockage Vectoriel"
        VDB[LlamaIndex Vector Store]
        IDX[Index Vectoriel]
        META[Métadonnées]
    end
    
    subgraph "Moteur de Recherche"
        QE[Query Engine]
        RET[Retriever]
        SIM[Similarité Sémantique]
    end
    
    POL --> DL
    STD --> DL
    UC --> DL
    WEB --> DL
    
    DL --> EM
    EM --> CS
    CS --> VDB
    
    VDB --> IDX
    VDB --> META
    
    IDX --> QE
    META --> QE
    QE --> RET
    RET --> SIM
```

### Flux de Traitement des Standards

```mermaid
stateDiagram-v2
    [*] --> Recherche_Web
    Recherche_Web --> Extraction_Contenu
    Extraction_Contenu --> Analyse_Changements
    Analyse_Changements --> Nouvelle_Version : Changements détectés
    Analyse_Changements --> Pas_de_Changement : Aucun changement
    Nouvelle_Version --> Mise_à_Jour_VectorDB
    Mise_à_Jour_VectorDB --> Notification
    Notification --> [*]
    Pas_de_Changement --> [*]
    
    state Analyse_Changements {
        [*] --> Calcul_Similarité
        Calcul_Similarité --> Comparaison_Seuil
        Comparaison_Seuil --> Détection_Différences
        Détection_Différences --> [*]
    }
```

## Configuration et Déploiement

### Variables d'Environnement Requises

```bash
# Configuration LLM
GEMINI_API_KEY=your_gemini_api_key

# Configuration Base de Données
STANDARDS_PATH=./db/llamaindex_store_standards
POLICIES_PATH=./db/llamaindex_store_policies
STANDARDS_VERSIONS_PATH=./db/standards_versions
STANDARDS_CHANGES_PATH=./db/standards_changes

# Configuration Embeddings
EMBEDDING_MODEL=BAAI/bge-m3
SIMILARITY_THRESHOLD=0.75

# Configuration API
API_HOST=0.0.0.0
API_PORT=8000
```

### Architecture de Déploiement

```mermaid
graph TB
    subgraph "Environnement de Production"
        LB[Load Balancer]
        
        subgraph "Services d'Application"
            API1[API FastAPI - Instance 1]
            API2[API FastAPI - Instance 2]
            API3[API FastAPI - Instance 3]
        end
        
        subgraph "Services de Données"
            VDB[Vector Database Cluster]
            FS[File Storage System]
            CACHE[Redis Cache]
        end
        
        subgraph "Services de Surveillance"
            MON[Monitoring]
            LOG[Logging]
            ALERT[Alertes]
        end
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> VDB
    API2 --> VDB
    API3 --> VDB
    
    API1 --> FS
    API2 --> FS
    API3 --> FS
    
    API1 --> CACHE
    API2 --> CACHE
    API3 --> CACHE
    
    API1 --> MON
    API2 --> LOG
    API3 --> ALERT
```

## Conclusion

Cette architecture multi-agents offre une solution robuste et extensible pour l'évaluation automatisée des politiques de sécurité et l'analyse des cas d'usage dans le secteur bancaire. Le système de versioning des standards assure une veille technologique continue et maintient la conformité aux dernières exigences réglementaires.

Les points forts du système incluent :

1. **Modularité** : Chaque agent est spécialisé dans une tâche spécifique
2. **Extensibilité** : Nouveaux agents facilement intégrables
3. **Robustesse** : Gestion d'erreurs et retry automatique
4. **Performance** : Traitement parallèle et mise en cache
5. **Conformité** : Adaptation spécifique aux exigences bancaires
6. **Traçabilité** : Versioning complet des standards et changements

Cette documentation technique constitue le livrable pour la compréhension et la maintenance du système GRC Assistant.
