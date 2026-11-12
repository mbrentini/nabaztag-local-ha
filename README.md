# Nabaztag Local — intégration Home Assistant

Intégration HACS pour piloter un Nabaztag / Nabaztag:tag via l'API HTTP locale du serveur [nabaztag-violet](https://github.com/ClaraVnk/nabaztag/tree/main/nabaztag-violet). Elle utilise l'API du serveur local, pas les routes du service Terrier.

## Installation et configuration

1. Dans HACS → Intégrations → ⋮ → Dépôts personnalisés, ajouter `https://github.com/mbrentini/nabaztag-local-ha`, catégorie **Intégration**.
2. Installer **Nabaztag Local**, redémarrer Home Assistant et ajouter l'intégration.
3. Saisir l'adresse IP du serveur Nabaztag, par exemple `http://192.168.3.10:8099`. **L'adresse IP est recommandée plutôt que le nom DNS**, car un nom résolu par le navigateur peut ne pas l'être depuis l'environnement réseau de Home Assistant.
4. Si l'option `api_token` est activée sur le serveur, saisir le même jeton.
5. Si plusieurs lapins sont connectés au serveur, renseigner leur adresse MAC (12 caractères hexadécimaux, sans séparateurs). Laisser vide lorsqu'un seul lapin est connecté.

> L'adresse IP utilisée ici est celle de l'API de contrôle appelée par Home Assistant. Elle est distincte de `server_address` dans les options de l'add-on Nabaztag Violet : ce dernier doit rester un nom DNS résolvable par le lapin pour sa connexion XMPP.

## Entités Home Assistant

- **Binaire** : lapin connecté.
- **Capteurs** : nombre de lapins connectés, adresse serveur, compteurs du microphone, métadonnées du dernier enregistrement push-to-talk et nombre/état des clés d'adoption.
- **Lumières RGB** : cinq entités indépendantes pour les LED basse (`bottom`), gauche (`left`), centrale (`middle`), droite (`right`) et haute (`top`). L'entité de la LED basse conserve l'identifiant unique historique de la lumière du ventre afin de réutiliser l'entité déjà créée.
- **Interrupteurs** : sommeil / réveil et écoute passive du microphone.
- **Nombres** : volume du haut-parleur (0–100) et positions des oreilles (0–16).
- **Sélecteurs** : icône météo du ventre et nez (aucun, clignotement, double clignotement).
- **Boutons** : jingles intégrés, interrogation de l'état et comportement spontané.

## Affichage météo automatique

Dans **Paramètres → Appareils et services → Nabaztag Local → Configurer**, sélectionner une entité Home Assistant de domaine `weather`. L'intégration lit son état au démarrage puis à chaque heure pile et met à jour l'icône du ventre.

| Condition Home Assistant | Icône du Nabaztag |
|---|---|
| `sunny`, `clear-night` | `sun` |
| `partlycloudy`, `cloudy`, `windy` | `cloudy` |
| `fog` | `smog` |
| `rainy`, `pouring` | `rain` |
| `snowy`, `snowy-rainy` | `snow` |
| `lightning`, `lightning-rainy`, `hail` | `storm` |

Les états non reconnus sont ignorés. Cette fonction lit la condition courante de l'entité météo ; elle ne calcule pas de prévision.

## Services avancés

Tous les services sont sous le domaine `nabaztag_local`. Les champs de `say` et `play` sont directement éditables dans le formulaire d'action Home Assistant :

- `say` : fait prononcer un texte saisi dans le champ **Texte** (voix, vitesse, hauteur, attente). `speak` reste disponible comme alias historique.
- `play` : lecture d'une URL MP3/WAV saisie dans le champ **URL audio**.
- `move_ears`, `wiggle_ears` : positionnement précis ou frétillement Ambient des oreilles.
- `set_led` : commande RGB de chacune des cinq LED (`bottom`, `left`, `middle`, `right`, `top`).
- `set_bottom_led` : couleur de la LED basse par index de palette Ambient.
- `send_choreography`, `send_program`, `send_ambient`, `send_raw_packet` : commandes Violet avancées.
- `download_recording` : télécharge le dernier push-to-talk dans `/config/www`, accessible ensuite via `/local/<nom-du-fichier>`.
- `adoption_action` : confirmer/refuser/oublier une clé Naboot. Pour confirmer ou refuser, il faut fournir l'empreinte affichée par la page d'adoption du serveur et comparer visuellement les cinq couleurs.
- `stage_ota` : préparer un firmware signé déjà présent sur le système de fichiers du serveur Nabaztag. Le déclenchement dépend du runtime et du firmware du lapin.

Les commandes `/api/status`, `/api/say`, `/api/play`, `/api/jingle`, `/api/volume`, `/api/ears`, `/api/led`, `/api/choreography`, `/api/program`, `/api/weather`, `/api/nose`, `/api/bottomled`, `/api/earwiggle`, `/api/sleep`, `/api/state`, `/api/lastrecording`, `/api/ambient`, `/api/raw`, `/api/mic`, `/api/personality`, `/api/adoption` et `/api/ota` sont couvertes par les entités, services ou capteurs ci-dessus.

## Événements physiques du lapin

Le serveur peut émettre l'événement Home Assistant `nabaztag_event` pour les appuis sur le bouton, les tags RFID/Ztamp et les mouvements manuels des oreilles. Exemple d'automatisation :

```yaml
triggers:
  - trigger: event
    event_type: nabaztag_event
    event_data:
      type: button
      action: click
actions:
  - action: light.toggle
    target:
      entity_id: light.salon
```

Pour un tag RFID, le type d'événement est `rfid` et l'identifiant est dans `trigger.event.data.tag`. Pour les oreilles, le type est `ears` avec les positions `left` et `right`.

## Pipeline vocal et options propres à l'add-on

Le pipeline push-to-talk → Whisper → agent de conversation → TTS est configuré dans les **options de l'add-on Nabaztag Violet**, pas par l'API de contrôle de cette intégration. Les options documentées incluent `voice_pipeline`, `conversation_agent`, `stt_language`, `stt_model`, `tts_engine`, `tts_entity` et `voice_pitch`.

L'écoute passive (« Nabi ») est commandée ici à l'exécution par l'interrupteur **Écoute passive** ; elle est désactivée par défaut pour préserver la confidentialité. Le mot de réveil, le modèle STT, le moteur TTS, le jingle de connexion et le niveau de personnalité restent des options de l'add-on.

## Sécurité et limites

L'API est ouverte par défaut sur le réseau local. Si `api_token` est activé côté serveur, renseigner le même jeton dans l'intégration. Ne pas exposer le port 8099 directement sur Internet.

La documentation complète de référence est [nabaztag-violet/DOCS.md](https://github.com/ClaraVnk/nabaztag/blob/main/nabaztag-violet/DOCS.md). Cette intégration suit les routes documentées, mais n'a pas encore été validée sur toutes les combinaisons de firmware et de lapins ; les fonctions de microphone, OTA et adoption nécessitent notamment les versions compatibles décrites par le projet serveur.
