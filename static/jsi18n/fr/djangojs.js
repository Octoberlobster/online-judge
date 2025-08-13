

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n > 1);
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "%(cnt)d submission in %(year)d": [
      "%(cnt)d soumission en %(year)d",
      "%(cnt)d soumissions en %(year)d"
    ],
    "%(cnt)d submission in the last year": [
      "%(cnt)d soumission l'ann\u00e9e derni\u00e8re",
      "%(cnt)d soumissions l'ann\u00e9e derni\u00e8re"
    ],
    "%(cnt)d submission on %(date)s": [
      "%(cnt)d soumission le %(date)s",
      "%(cnt)d soumissions le %(date)s"
    ],
    "%(cnt)d total submission": [
      "%(cnt)d soumission au total",
      "%(cnt)d soumissions au total"
    ],
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9",
      "%(sel)s sur %(cnt)s s\u00e9lectionn\u00e9s"
    ],
    "6 a.m.": "6:00",
    "6 p.m.": "18:00",
    "April": "Avril",
    "August": "Ao\u00fbt",
    "Available %s": "%s disponible(s)",
    "Cancel": "Annuler",
    "Choose": "Choisir",
    "Choose a Date": "Choisir une date",
    "Choose a Time": "Choisir une heure",
    "Choose a time": "Choisir une heure",
    "Choose all": "Tout choisir",
    "Chosen %s": "Choix des \u00ab\u00a0%s \u00bb",
    "Click to choose all %s at once.": "Cliquez pour choisir tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "Click to remove all chosen %s at once.": "Cliquez pour enlever tous les \u00ab\u00a0%s\u00a0\u00bb en une seule op\u00e9ration.",
    "December": "D\u00e9cembre",
    "Edit points vote (%s)": "Modifier le vote de points (%s)",
    "February": "F\u00e9vrier",
    "Filter": "Filtrer",
    "Hide": "Masquer",
    "January": "Janvier",
    "July": "Juillet",
    "June": "Juin",
    "March": "Mars",
    "May": "Mai",
    "Midnight": "Minuit",
    "Noon": "Midi",
    "Note: You are %s hour ahead of server time.": [
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heure.",
      "Note\u00a0: l'heure du serveur pr\u00e9c\u00e8de votre heure de %s heures."
    ],
    "Note: You are %s hour behind server time.": [
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heure.",
      "Note\u00a0: votre heure pr\u00e9c\u00e8de l'heure du serveur de %s heures."
    ],
    "November": "Novembre",
    "Now": "Maintenant",
    "Number of votes for this point value": "Nombre de votes pour cette valeur de points",
    "October": "Octobre",
    "Remove": "Enlever",
    "Remove all": "Tout enlever",
    "September": "Septembre",
    "Show": "Afficher",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ceci est une liste des \u00ab\u00a0%s\u00a0\u00bb disponibles. Vous pouvez en choisir en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab\u00a0Choisir\u00a0\u00bb entre les deux zones.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ceci est la liste des \u00ab\u00a0%s\u00a0\u00bb choisi(e)s. Vous pouvez en enlever en les s\u00e9lectionnant dans la zone ci-dessous, puis en cliquant sur la fl\u00e8che \u00ab Enlever \u00bb entre les deux zones.",
    "Today": "Aujourd'hui",
    "Tomorrow": "Demain",
    "Type into this box to filter down the list of available %s.": "\u00c9crivez dans cette zone pour filtrer la liste des \u00ab\u00a0%s\u00a0\u00bb disponibles.",
    "Unable to cast vote: %s": "Impossible de voter : %s",
    "Unable to delete vote: %s": "Impossible de supprimer le vote : %s",
    "Vote on problem points": "Voter sur les points du probl\u00e8me",
    "Yesterday": "Hier",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\u4f60\u5df2\u9078\u4e86\u4e00\u500b\u52d5\u4f5c, \u4f46\u6c92\u6709\u4efb\u4f55\u6539\u8b8a\u3002\u4f60\u53ef\u80fd\u52d5\u5230 '\u53bb' \u6309\u9215, \u800c\u4e0d\u662f '\u5132\u5b58' \u6309\u9215\u3002",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Vous avez s\u00e9lectionn\u00e9 une action, et vous n'avez fait aucune modification sur des champs. Vous cherchez probablement le bouton Envoyer et non le bouton Enregistrer.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\u4f60\u5df2\u9078\u4e86\u4e00\u500b\u52d5\u4f5c, \u4f46\u6709\u4e00\u500b\u53ef\u7de8\u8f2f\u6b04\u4f4d\u7684\u8b8a\u66f4\u5c1a\u672a\u5132\u5b58\u3002\u8acb\u9ede\u9078 OK \u9032\u884c\u5132\u5b58\u3002\u4f60\u9700\u8981\u91cd\u65b0\u57f7\u884c\u8a72\u52d5\u4f5c\u3002",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Vous avez s\u00e9lectionn\u00e9 une action, mais vous n'avez pas encore enregistr\u00e9 certains champs modifi\u00e9s. Cliquez sur OK pour enregistrer. Vous devrez r\u00e9appliquer l'action.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Vous avez des modifications non sauvegard\u00e9es sur certains champs \u00e9ditables. Si vous lancez une action, ces modifications vont \u00eatre perdues.",
    "abbrev. month April\u0004Apr": "avr",
    "abbrev. month August\u0004Aug": "ao\u00fb",
    "abbrev. month December\u0004Dec": "d\u00e9c",
    "abbrev. month February\u0004Feb": "f\u00e9v",
    "abbrev. month January\u0004Jan": "jan",
    "abbrev. month July\u0004Jul": "jui",
    "abbrev. month June\u0004Jun": "jun",
    "abbrev. month March\u0004Mar": "mar",
    "abbrev. month May\u0004May": "mai",
    "abbrev. month November\u0004Nov": "nov",
    "abbrev. month October\u0004Oct": "oct",
    "abbrev. month September\u0004Sep": "sep",
    "one letter Friday\u0004F": "V",
    "one letter Monday\u0004M": "L",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "D",
    "one letter Thursday\u0004T": "J",
    "one letter Tuesday\u0004T": "M",
    "one letter Wednesday\u0004W": "M",
    "past year": "ann\u00e9e derni\u00e8re",
    "time format with day\u0004%d day %h:%m:%s": [
      "%d jour %h:%m:%s",
      "%d jours %h:%m:%s"
    ],
    "time format without day\u0004%h:%m:%s": "%h:%m:%s"
  };
  for (const key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      const value = django.catalog[msgid];
      if (typeof value === 'undefined') {
        return msgid;
      } else {
        return (typeof value === 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      const value = django.catalog[singular];
      if (typeof value === 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value.constructor === Array ? value[django.pluralidx(count)] : value;
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      let value = django.gettext(context + '\x04' + msgid);
      if (value.includes('\x04')) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      let value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.includes('\x04')) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "j F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%d.%m.%Y %H:%M:%S",
      "%d.%m.%Y %H:%M:%S.%f",
      "%d.%m.%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%d.%m.%Y",
      "%d.%m.%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j N Y H:i",
    "SHORT_DATE_FORMAT": "j N Y",
    "THOUSAND_SEPARATOR": "\u00a0",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      const value = django.formats[format_type];
      if (typeof value === 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }
};

