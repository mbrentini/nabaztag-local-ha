# Nabaztag Local — intégration Home Assistant

Intégration HACS pour piloter un Nabaztag / Nabaztag:tag via l'API HTTP locale du serveur [nabaztag-violet](https://github.com/ClaraVnk/nabaztag/tree/main/nabaztag-violet).

L'intégration utilise les routes du serveur local, et non celles du service Terrier.

## Installation

1. Dans HACS → Intégrations → ⋮ → Dépôts personnalisés.
2. Ajouter `https://github.com/mbrentini/nabaztag-local-ha`, catégorie **Intégration**.
3. Installer **Nabaztag Local**, puis redémarrer Home Assistant.
4. Ajouter l'intégration depuis **Paramètres → Appareils et services → Ajouter une intégration**.
5. Saisir l'URL du serveur, par exemple `http://192.168.1.20:8099`.

L'URL doit pointer vers le port HTTP de l'API de contrôle (8099 par défaut sur l'hôte, 8080 dans le conteneur de l'add-on).

## Entités

- **Binaire** : lapin connecté.
- **Capteurs** : nombre de lapins connectés et adresse du serveur.
- **Lumière RGB** : LED du ventre.
- **Interrupteur** : sommeil / réveil.
- **Nombre** : volume du haut-parleur (0 à 100).
- **Sélecteur** : icône météo du ventre (soleil, nuage, brume, pluie, neige, orage).
- **Boutons** : jingles intégrés du Nabaztag.

## Service vocal

L'action `nabaztag_local.speak` permet de faire prononcer un texte par le lapin :

```yaml
action:
  - action: nabaztag_local.speak
    data:
      text: "Bonjour, la maison !"
      voice: fr
      speed: 160
      pitch: 50
```

Les paramètres `voice`, `speed` et `pitch` sont facultatifs.

## Sécurité

Le serveur local n'exige aucun jeton par défaut. Il peut toutefois être configuré avec `api_token`. Cette version de l'intégration utilise le mode sans jeton ; n'expose pas le port de contrôle directement sur Internet.

## API utilisée

Les chemins et paramètres sont alignés sur le code et la documentation de `nabaztag-violet` : `/api/status`, `/api/say`, `/api/jingle`, `/api/led`, `/api/weather`, `/api/sleep` et `/api/volume`.
