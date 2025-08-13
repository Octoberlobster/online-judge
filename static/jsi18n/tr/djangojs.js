

'use strict';
{
  const globals = this;
  const django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    const v = (n != 1);
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
      "%(sel)s / %(cnt)s se\u00e7ildi",
      "%(sel)s / %(cnt)s se\u00e7ildi"
    ],
    "6 a.m.": "Sabah 6",
    "6 p.m.": "6 \u00f6.s.",
    "April": "Nisan",
    "August": "A\u011fustos",
    "Available %s": "Mevcut %s",
    "Cancel": "\u0130ptal",
    "Choose": "Se\u00e7in",
    "Choose a Date": "Bir Tarih Se\u00e7in",
    "Choose a Time": "Bir Saat Se\u00e7in",
    "Choose a time": "Bir saat se\u00e7in",
    "Choose all": "T\u00fcm\u00fcn\u00fc se\u00e7in",
    "Chosen %s": "Se\u00e7ilen %s",
    "Click to choose all %s at once.": "Bir kerede t\u00fcm %s se\u00e7ilmesi i\u00e7in t\u0131klay\u0131n.",
    "Click to remove all chosen %s at once.": "Bir kerede t\u00fcm se\u00e7ilen %s kald\u0131r\u0131lmas\u0131 i\u00e7in t\u0131klay\u0131n.",
    "December": "Aral\u0131k",
    "February": "\u015eubat",
    "Filter": "S\u00fczge\u00e7",
    "Hide": "Gizle",
    "January": "Ocak",
    "July": "Temmuz",
    "June": "Haziran",
    "March": "Mart",
    "May": "May\u0131s",
    "Midnight": "Geceyar\u0131s\u0131",
    "Noon": "\u00d6\u011fle",
    "Note: You are %s hour ahead of server time.": [
      "Not: Sunucu saatinin %s saat ilerisindesiniz.",
      "Not: Sunucu saatinin %s saat ilerisindesiniz."
    ],
    "Note: You are %s hour behind server time.": [
      "Not: Sunucu saatinin %s saat gerisindesiniz.",
      "Not: Sunucu saatinin %s saat gerisindesiniz."
    ],
    "November": "Kas\u0131m",
    "Now": "\u015eimdi",
    "October": "Ekim",
    "Remove": "Kald\u0131r",
    "Remove all": "T\u00fcm\u00fcn\u00fc kald\u0131r",
    "September": "Eyl\u00fcl",
    "Show": "G\u00f6ster",
    "This is the list of available %s. You may choose some by selecting them in the box below and then clicking the \"Choose\" arrow between the two boxes.": "Bu mevcut %s listesidir. A\u015fa\u011f\u0131daki kutudan baz\u0131lar\u0131n\u0131 i\u015faretleyerek ve ondan sonra iki kutu aras\u0131ndaki \"Se\u00e7in\" okuna t\u0131klayarak se\u00e7ebilirsiniz.",
    "This is the list of chosen %s. You may remove some by selecting them in the box below and then clicking the \"Remove\" arrow between the two boxes.": "Bu se\u00e7ilen %s listesidir. A\u015fa\u011f\u0131daki kutudan baz\u0131lar\u0131n\u0131 i\u015faretleyerek ve ondan sonra iki kutu aras\u0131ndaki \"Kald\u0131r\" okuna t\u0131klayarak kald\u0131rabilirsiniz.",
    "Today": "Bug\u00fcn",
    "Tomorrow": "Yar\u0131n",
    "Type into this box to filter down the list of available %s.": "Mevcut %s listesini s\u00fczmek i\u00e7in bu kutu i\u00e7ine yaz\u0131n.",
    "Yesterday": "D\u00fcn",
    "You have selected an action, and you haven't made any changes on individual fields. You're probably looking for the Go button rather than the Save button.": "\u4f60\u5df2\u9078\u4e86\u4e00\u500b\u52d5\u4f5c, \u4f46\u6c92\u6709\u4efb\u4f55\u6539\u8b8a\u3002\u4f60\u53ef\u80fd\u52d5\u5230 '\u53bb' \u6309\u9215, \u800c\u4e0d\u662f '\u5132\u5b58' \u6309\u9215\u3002",
    "You have selected an action, and you haven\u2019t made any changes on individual fields. You\u2019re probably looking for the Go button rather than the Save button.": "Bir eylem se\u00e7tiniz, ancak tek tek alanlarda herhangi bir de\u011fi\u015fiklik yapmad\u0131n\u0131z. Muhtemelen Kaydet d\u00fc\u011fmesi yerine Git d\u00fc\u011fmesini ar\u0131yorsunuz.",
    "You have selected an action, but you haven't saved your changes to individual fields yet. Please click OK to save. You'll need to re-run the action.": "\u4f60\u5df2\u9078\u4e86\u4e00\u500b\u52d5\u4f5c, \u4f46\u6709\u4e00\u500b\u53ef\u7de8\u8f2f\u6b04\u4f4d\u7684\u8b8a\u66f4\u5c1a\u672a\u5132\u5b58\u3002\u8acb\u9ede\u9078 OK \u9032\u884c\u5132\u5b58\u3002\u4f60\u9700\u8981\u91cd\u65b0\u57f7\u884c\u8a72\u52d5\u4f5c\u3002",
    "You have selected an action, but you haven\u2019t saved your changes to individual fields yet. Please click OK to save. You\u2019ll need to re-run the action.": "Bir eylem se\u00e7tiniz, ancak de\u011fi\u015fikliklerinizi tek tek alanlara kaydetmediniz. Kaydetmek i\u00e7in l\u00fctfen TAMAM d\u00fc\u011fmesine t\u0131klay\u0131n. Eylemi yeniden \u00e7al\u0131\u015ft\u0131rman\u0131z gerekecek.",
    "You have unsaved changes on individual editable fields. If you run an action, your unsaved changes will be lost.": "Bireysel d\u00fczenlenebilir alanlarda kaydedilmemi\u015f de\u011fi\u015fiklikleriniz var. E\u011fer bir eylem \u00e7al\u0131\u015ft\u0131r\u0131rsan\u0131z, kaydedilmemi\u015f de\u011fi\u015fiklikleriniz kaybolacakt\u0131r.",
    "abbrev. month April\u0004Apr": "Nis",
    "abbrev. month August\u0004Aug": "A\u011fu",
    "abbrev. month December\u0004Dec": "Ara",
    "abbrev. month February\u0004Feb": "\u015eub",
    "abbrev. month January\u0004Jan": "Oca",
    "abbrev. month July\u0004Jul": "Tem",
    "abbrev. month June\u0004Jun": "Haz",
    "abbrev. month March\u0004Mar": "Mar",
    "abbrev. month May\u0004May": "May",
    "abbrev. month November\u0004Nov": "Kas",
    "abbrev. month October\u0004Oct": "Eki",
    "abbrev. month September\u0004Sep": "Eyl",
    "one letter Friday\u0004F": "C",
    "one letter Monday\u0004M": "Pt",
    "one letter Saturday\u0004S": "Ct",
    "one letter Sunday\u0004S": "P",
    "one letter Thursday\u0004T": "Pe",
    "one letter Tuesday\u0004T": "S",
    "one letter Wednesday\u0004W": "\u00c7",
    "time format with day\u0004%d day %h:%m:%s": [
      "%d g\u00fcn, %h:%m:%s",
      "%d g\u00fcn, %h:%m:%s"
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
    "DATETIME_FORMAT": "d F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%Y %H:%M",
      "%Y-%m-%d %H:%M:%S",
      "%Y-%m-%d %H:%M:%S.%f",
      "%Y-%m-%d %H:%M",
      "%Y-%m-%d"
    ],
    "DATE_FORMAT": "d F Y",
    "DATE_INPUT_FORMATS": [
      "%d/%m/%Y",
      "%d/%m/%y",
      "%y-%m-%d",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": 1,
    "MONTH_DAY_FORMAT": "d F",
    "NUMBER_GROUPING": 3,
    "SHORT_DATETIME_FORMAT": "d M Y H:i",
    "SHORT_DATE_FORMAT": "d M Y",
    "THOUSAND_SEPARATOR": ".",
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

