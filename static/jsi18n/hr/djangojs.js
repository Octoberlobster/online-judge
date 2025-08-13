

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
      "odabrano %(sel)s od %(cnt)s",
      "odabrano %(sel)s od %(cnt)s",
      "odabrano %(sel)s od %(cnt)s"
    ],
    "6 a.m.": "6 ujutro",
    "6 p.m.": "6 popodne",
    "April": "\u56db\u6708",
    "August": "\u516b\u6708",
    "Available %s": "Dostupno %s",
    "Cancel": "Odustani",
    "Choose": "Izaberi",
    "Choose a Date": "Odaberite datum",
    "Choose a Time": "Izaberite vrijeme",
    "Choose a time": "Izaberite vrijeme",
    "Choose all": "Odaberi sve",
    "Chosen %s": "Odabrano %s",
    "Click to choose all %s at once.": "Kliknite da odabrete sve %s odjednom.",
    "Click to remove all chosen %s at once.": "Kliknite da uklonite sve izabrane %s odjednom.",
    "December": "\u5341\u4e8c\u6708",
    "February": "\u4e8c\u6708",
    "Filter": "Filter",
    "Hide": "Sakri",
    "January": "\u4e00\u6708",
    "July": "\u4e03\u6708",
    "June": "\u516d\u6708",
    "March": "\u4e09\u6708",
    "May": "\u4e94\u6708",
    "Midnight": "Pono\u0107",
    "Noon": "Podne",
    "Note: You are %s hour ahead of server time.": [
      "\u5099\u8a3b\uff1a\u60a8\u7684\u96fb\u8166\u6642\u9593\u6bd4\u4f3a\u670d\u5668\u5feb %s \u5c0f\u6642\u3002",
      "",
      ""
    ],
    "Note: You are %s hour behind server time.": [
      "\u5099\u8a3b\uff1a\u60a8\u7684\u96fb\u8166\u6642\u9593\u6bd4\u4f3a\u670d\u5668\u6162 %s \u5c0f\u6642\u3002",
      "",
      ""
    ],
    "November": "\u5341\u4e00\u6708",
    "Now": "Sada",
    "October": "\u5341\u6708",
    "Remove": "Ukloni",
    "Remove all": "Ukloni sve",
    "September": "\u4e5d\u6708",
    "Show": "Prika\u017ei",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Ovo je popis dostupnih %s. Mo\u017eete dodati pojedine na na\u010din da ih izaberete u polju ispod i kliknete \"Izaberi\" strelicu izme\u0111u dva polja. ",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Ovo je popis odabranih %s. Mo\u017eete ukloniti pojedine na na\u010din da ih izaberete u polju ispod i kliknete \"Ukloni\" strelicu izme\u0111u dva polja. ",
    "Today": "Danas",
    "Tomorrow": "Sutra",
    "Type into this box to filter down the list of available %s.": "Tipkajte u ovo polje da filtrirate listu dostupnih %s.",
    "Yesterday": "Ju\u010der",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "Odabrali ste akciju, a niste napravili nikakve izmjene na pojedinim poljima. Vjerojatno tra\u017eite gumb Idi umjesto gumb Spremi.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "Odabrali ste akciju, ali niste jo\u0161 spremili promjene na pojedinim polja. Molimo kliknite OK za spremanje. Morat \u0107ete ponovno pokrenuti akciju.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Neke promjene nisu spremljene na pojedinim polja za ure\u0111ivanje. Ako pokrenete akciju, nespremljene promjene \u0107e biti izgubljene.",
    "one letter Friday\u0004F": "\u4e94",
    "one letter Monday\u0004M": "\u4e00",
    "one letter Saturday\u0004S": "\u516d",
    "one letter Sunday\u0004S": "\u65e5",
    "one letter Thursday\u0004T": "\u56db",
    "one letter Tuesday\u0004T": "\u4e8c",
    "one letter Wednesday\u0004W": "\u4e09",
    "time format with day\u0004%d day %h:%m:%s": [
      "%d dan %h:%m:%s",
      "%d dana %h:%m:%s",
      "%d dana %h:%m:%s"
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
    "DATETIME_FORMAT": "j. E Y. H:i",
    "DATETIME_INPUT_FORMATS": [
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
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
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "j. E Y.",
    "DATE_INPUT_FORMATS": [
      "%Y-%m-%d",
      "%d.%m.%Y.",
      "%d.%m.%y.",
      "%d. %m. %Y.",
      "%d. %m. %y."
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

