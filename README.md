# Nabaztag Local — intégration Home Assistant

Intégration HACS pour piloter un Nabaztag / Nabaztag:tag via l'API HTTP locale du serveur [nabaztag-violet](https://github.com/ClaraVnk/nabaztag/tree/main/nabaztag-violet).

Cette intégration ne reprend pas les routes HTTP de Terrier : elle utilise directement les endpoints documentés par le serveur local.

## Installation

1. Dans HACS → Intégrations → ⋮ → Dépôts personnalisés.
2. Ajouter `https://github.com/mbrentini/nabaztag-local-ha`, catégorie **Intégration**.
3. Installer **Nabaztag Local** puis redémarrer Home Assistant.
4. Ajouter l'intégration depuis **Paramètres → Appareils et services → Ajouter une intégration**.
5. Saisir l'URL du serveur, par exemple `http://192.168.1.20:8099`.

L'URL doit pointer vers le port HTTP de l'API de contrôle (8099 par défaut sur l'hôte, 8080 dans le conteneur de l'add-on).

## Entités créées

- Binaire : lapin connecté.
- Capteurs : nombre de lapins connectés et adresse du serveur.
- Lumière RGB : LED du ventre (commande `/api/led?led=bottom`).
- Interrupteur : sommeil / réveil (`/api/sleep`).
- Nombre : volume du haut-parleur, de 0 à 100 (`/api/volume`).
- Sélecteur : icône météo du ventre (`/api/weather`).
- Boutons : jingles intégrés (`/api/jingle`).

La parole est disponible via l'action **Parler** exposée par le service Home Assistant `nabaztag_local.speak` (voir ci-dessous).

## Service parler

Exemple d'automatisation :

```yaml
action:
  - action: nabaztag_local.speak
    data:
      text: "Bonjour, la maison !"
```

Paramètres facultatifs : `voice` (fr), `speed` (160), `pitch` (50).

## Sécurité

Le serveur local n'exige aucun jeton par défaut. Il peut toutefois être configuré avec `api_token`. Cette première version de l'intégration suppose l'API sans jeton ; n'expose pas le port de contrôle directement sur Internet.

## API vérifiée

Les chemins et paramètres utilisés correspondent à la documentation de `nabaztag-violet` : `/api/status`, `/api/say`, `/api/jingle`, `/api/led`, `/api/weather`, `/api/sleep`, `/api/volume`.
