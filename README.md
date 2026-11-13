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

- **Binaire** : connexion du lapin sélectionné par MAC, et non du premier lapin connecté.
- **Capteurs** : nombre de lapins, serveur, XMPP (état, durée de connexion, dernière activité), microphone, enregistrement vocal, adoption, dernier RFID, bouton et oreilles.
- **Lumières RGB** : cinq entités indépendantes pour les LED basse (`bottom`), gauche (`left`), centrale (`middle`), droite (`right`) et haute (`top`). L'entité de la LED basse conserve l'identifiant unique historique de la lumière du ventre afin de réutiliser l'entité déjà créée.
- **Interrupteurs** : sommeil / réveil et écoute passive du microphone.
- **Nombres** : volume (0–100), oreilles gauche/droite (0–16), sens de rotation (0/1), palette LED basse (0–255), vitesse et hauteur de synthèse vocale.
- **Sélecteurs** : icône météo du ventre, nez (aucun, clignotement, double clignotement), jingle à tester.
- **Boutons** : jingles intégrés, prévisualisation du jingle choisi, frétillement des oreilles, interrogation de l'état et comportement spontané.
- **Texte** : message à dire, voix, **Radio — URL du flux audio**, chorégraphie, programme, paquet Base64 et paires Ambient.
- **Événements natifs** : clic/double-clic sur la tête, lecture RFID et mouvement manuel des oreilles.

## Radio enregistrée dans la configuration

Dans **Paramètres → Appareils et services → Nabaztag Local → Configurer**, une nouvelle option **URL du flux radio** accepte une adresse HTTP(S) directe vers un média audio supporté. L'URL est conservée dans les options de l'intégration. Le bouton **Lire la radio configurée** sur l'appareil lance sa lecture via `/api/play`. Il n'existe pas de retour de lecture dans l'API locale. L'entité texte existante **Radio — URL du flux audio** reste disponible pour envoyer ponctuellement une autre URL sans modifier la radio enregistrée. L'identifiant unique `play_url` ne change pas.

## Affichage météo automatique

Choisir une entité `weather.*` soit dans **Paramètres → Appareils et services → Nabaztag Local → Configurer**, soit directement sur l'appareil avec le sélecteur **Source météo Home Assistant**. La sélection est enregistrée dans les options de l'intégration et recharge son suivi météo.

La synchronisation utilise la **condition actuelle** de l'entité météo (pas les prévisions) et envoie un `GET /api/weather?v=<icône>` au serveur :
- immédiatement au démarrage ou au changement de source ;
- à chaque changement d'état de la météo dans Home Assistant ;
- au minimum une fois par heure.

Le bouton **Synchroniser la météo** force également un envoi immédiat. Le sélecteur **Icône météo du ventre** permet une commande manuelle, mais la prochaine synchronisation automatique peut écraser cette sélection. Choisir **Désactivée** comme source météo pour conserver un contrôle manuel.

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


## Entités de commande et confidentialité

Une valeur envoyée à l'entité **Dire un texte** prononce immédiatement le texte sur le lapin ; le champ **Lire une URL audio** lance directement la lecture. Ces entités acceptent également `text.set_value` dans les automatisations. La voix et les nombres de vitesse/hauteur sont les paramètres par défaut des commandes émises par le champ texte. Les actions `nabaztag_local.say`, `nabaztag_local.speak` et `nabaztag_local.play` conservent leurs paramètres propres.

Le champ **Paquet Ambient** attend des paires `service=valeur` séparées par des virgules, par exemple `8=1,9=2`. Les champs texte sont limités à 255 caractères par Home Assistant ; utiliser les actions pour les programmes, chorégraphies et paquets plus longs. Les opérations à risques (adoption, OTA), qui nécessitent des paramètres de sécurité, restent des **actions explicites** plutôt que des interrupteurs déclenchant un flash ou une confirmation sans précaution.

Les états des LED et de certaines commandes restent **optimistes**, puisque l'API locale ne renvoie pas systématiquement leur état matériel. Les options locales de synthèse ne sont pas enregistrées côté serveur. Attention : Home Assistant peut enregistrer les textes saisis dans l'historique Recorder. Éviter les données sensibles, ou exclure ces entités de Recorder.

Les actions comportent désormais un champ optionnel **Appareil Nabaztag**. S'il y a plusieurs entrées d'intégration, le choix de l'appareil est requis pour éviter qu'une commande soit envoyée au mauvais lapin.

## Migration depuis les YAML officiels et nettoyage des doublons

Le dossier officiel [`home-assistant/`](https://github.com/ClaraVnk/nabaztag/tree/main/home-assistant) fournit des **packages YAML** : `entities.yaml` ajoute des helpers et automatisations qui font double emploi avec les entités natives de cette intégration. Les scripts et automations des autres packages (`ambient.yaml`, `rfid.yaml`, `proactive.yaml`, `nabaztag_tasks.yaml`) sont des exemples utiles, mais doivent être adaptés si leurs commandes sont déjà couvertes par les nouvelles entités.

Cette version conserve les identifiants uniques existants, y compris `belly` pour la LED basse. Elle ne supprime pas automatiquement d'anciennes entités du registre Home Assistant. Si des doublons persistent, vérifier **Paramètres → Appareils et services → Nabaztag Local** : deux configurations pointant vers le même lapin (IP et alias DNS) peuvent en être la cause. Retirer uniquement l'entrée redondante, puis les anciennes entités indisponibles après vérification des automatisations. Le nouveau flux refuse une MAC déjà configurée lorsqu'elle est identifiable et exige une MAC s'il y a plusieurs lapins.

L'intégration HACS [`terrier-ha`](https://github.com/ClaraVnk/terrier-ha) est conçue pour le serveur Le Terrier et son README indique qu'elle **ne se connecte pas à l'add-on local** `nabaztag-violet`. Les réglages exclusifs à ce serveur (agenda, podcasts, planificateur, etc.) ne font donc pas partie des commandes de l'API locale.

## Tests

Une validation GitHub Actions compile le Python, exécute des tests unitaires d'identification/routage et parse les fichiers JSON/YAML. Elle ne remplace pas les essais sur un serveur et un lapin réels.

## Radio / URL audio

L'entité **Radio — URL du flux audio** accepte une URL HTTP(S) directe vers un flux MP3 ou un fichier WAV compatible. En validant le champ, l'intégration envoie la commande `/api/play?url=…`. L'identifiant unique historique `play_url` est conservé pour éviter un doublon lors de la mise à jour. Le même accès est disponible par l'action `nabaztag_local.play`, avec un champ URL. Le serveur Nabaztag doit pouvoir accéder au fichier ou au flux ; une page de lecteur web, un fichier AAC ou une playlist qui ne fournit pas directement un média compatible peuvent échouer. L'API locale ne documente pas de commande de lecture radio distincte ni de retour d'état de lecture ; il s'agit donc d'une **commande de lancement**, pas d'un lecteur média avec retour d'état.
