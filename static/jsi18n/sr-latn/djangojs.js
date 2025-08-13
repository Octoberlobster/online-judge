

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
    if (typeof v === 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  const newcatalog = {
    "%(sel)s of %(cnt)s selected": [
      "%(sel)s od %(cnt)s izabran",
      "%(sel)s od %(cnt)s izabrana",
      "%(sel)s od %(cnt)s izabranih"
    ],
    "6 a.m.": "18\u010d",
    "6 p.m.": "18\u010d",
    "April": "April",
    "August": "Avgust",
    "Available %s": "Dostupni %s",
    "Cancel": "Poni\u0161ti",
    "Choose": "Izaberi",
    "Choose a Date": "Odaberite datum",
    "Choose a Time": "Odaberite vreme",
    "Choose a time": "Odabir vremena",
    "Choose all": "Izaberi sve",
    "Chosen %s": "Izabrano \u201e%s\u201c",
    "Click to choose all %s at once.": "Izaberite sve \u201e%s\u201c odjednom.",
    "Click to remove all chosen %s at once.": "Uklonite sve izabrane \u201e%s\u201c odjednom.",
    "December": "Decembar",
    "February": "Februar",
    "Filter": "Filter",
    "Hide": "Sakrij",
    "January": "Januar",
    "July": "Jul",
    "June": "Jun",
    "March": "Mart",
    "May": "Maj",
    "Midnight": "Pono\u0107",
    "Noon": "Podne",
    "Note: You are %s hour ahead of server time.": [
      "Obave\u0161tenje: Vi ste %s sat ispred serverskog vremena.",
      "Obave\u0161tenje: Vi ste %s sata ispred serverskog vremena.",
      "Obave\u0161tenje: Vi ste %s sati ispred serverskog vremena."
    ],
    "Note: You are %s hour behind server time.": [
      "Obave\u0161tenje: Vi ste %s sat iza serverskog vremena.",
      "Obave\u0161tenje: Vi ste %s sata iza serverskog vremena.",
      "Obave\u0161tenje: Vi ste %s sati iza serverskog vremena."
    ],
    "November": "Novembar",
    "Now": "Trenutno vreme",
    "October": "Oktobar",
    "Remove": "Ukloni",
    "Remove all": "Ukloni sve",
    "September": "Septembar",
    "Show": "Poka\u017ei",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ovo je lista dostupnih \u201e%s\u201c. Mo\u017eete izabrati elemente tako \u0161to \u0107ete ih izabrati u listi i kliknuti na \u201eIzaberi\u201c.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ovo je lista izabranih \u201e%s\u201c. Mo\u017eete ukloniti elemente tako \u0161to \u0107ete ih izabrati u listi i kliknuti na \u201eUkloni\u201c.",
    "Today": "Danas",
    "Tomorrow": "Sutra",
    "Type into this box to filter down the list of available %s.": "Filtrirajte listu dostupnih elemenata \u201e%s\u201c.",
    "Yesterday": "Ju\u010de",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Izabrali ste akciju i niste napravili nijednu promenu na pojedina\u010dnim poljima. Verovatno tra\u017eite Kreni dugme umesto Sa\u010duvaj.",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Izabrali ste akciju, ali niste sa\u010duvali va\u0161e promene u pojedina\u010dna polja. Kliknite na OK da sa\u010duvate promene. Bi\u0107e neophodno da ponovo pokrenete akciju.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Imate nesa\u010divane izmene. Ako pokrenete akciju, izmene \u0107e biti izgubljene.",
    "abbrev. month April\u0004Apr": "apr",
    "abbrev. month August\u0004Aug": "avg",
    "abbrev. month December\u0004Dec": "dec",
    "abbrev. month February\u0004Feb": "feb",
    "abbrev. month January\u0004Jan": "jan",
    "abbrev. month July\u0004Jul": "jul",
    "abbrev. month June\u0004Jun": "jun",
    "abbrev. month March\u0004Mar": "mart",
    "abbrev. month May\u0004May": "maj",
    "abbrev. month November\u0004Nov": "nov",
    "abbrev. month October\u0004Oct": "okt",
    "abbrev. month September\u0004Sep": "sep",
    "one letter Friday\u0004F": "P",
    "one letter Monday\u0004M": "P",
    "one letter Saturday\u0004S": "S",
    "one letter Sunday\u0004S": "N",
    "one letter Thursday\u0004T": "\u010c",
    "one letter Tuesday\u0004T": "U",
    "one letter Wednesday\u0004W": "S"
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
    "DATETIME_FORMAT": "j. F Y. H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d.%m.%Y. %H:%M:%S",
      "%d.%m.%Y. %H:%M:%S.%f",
      "%d.%m.%Y. %H:%M",
      "%d.%m.%y. %H:%M:%S",
      "%d.%m.%y. %H:%M:%S.%f",
      "%d.%m.%y. %H:%M",
      "%d. %m. %Y. %H:%M:%S",
      "%d. %m. %Y. %H:%M:%S.%f",
      "%d. %m. %Y. %H:%M",
      "%d. %m. %y. %H:%M:%S",
      "%d. %m. %y. %H:%M:%S.%f",
      "%d. %m. %y. %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. F Y.",
    "DATE_INPUT_FORMATS": [
      "%d.%m.%Y.",
      "%d.%m.%y.",
      "%d. %m. %Y.",
      "%d. %m. %y.",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "j. F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "j.m.Y. H:i",
    "SHORT_DATE_FORMAT": "j.m.Y.",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y."
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

