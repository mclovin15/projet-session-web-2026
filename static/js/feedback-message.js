(function ($) {
  const FEEDBACK_STYLES = {
    success: {
      container: "border-green-200 bg-green-50 text-green-800",
      icon: "fa-circle-check text-green-600",
    },
    error: {
      container: "border-red-200 bg-red-50 text-red-700",
      icon: "fa-circle-xmark text-red-600",
    },
    warning: {
      container: "border-amber-200 bg-amber-50 text-amber-800",
      icon: "fa-triangle-exclamation text-amber-600",
    },
    info: {
      container: "border-sky-200 bg-sky-50 text-sky-800",
      icon: "fa-circle-info text-sky-600",
    },
  };

  const ALL_CONTAINER_CLASSES = Object.values(FEEDBACK_STYLES)
    .map((style) => style.container)
    .join(" ");
  const ALL_ICON_CLASSES = Object.values(FEEDBACK_STYLES)
    .map((style) => style.icon)
    .join(" ");

  function getMessageElement(target) {
    if (target && target.jquery) {
      return target.first();
    }

    return $(target).first();
  }

  function clearHideTimer($message) {
    const timerId = $message.data("feedbackHideTimer");

    if (timerId) {
      clearTimeout(timerId);
      $message.removeData("feedbackHideTimer");
    }
  }

  function applyStyle($message, type) {
    const style = FEEDBACK_STYLES[type] || FEEDBACK_STYLES.info;
    const $icon = $message.find(".feedback-message-icon");

    $message.removeClass(ALL_CONTAINER_CLASSES).addClass(style.container);
    $icon.removeClass(ALL_ICON_CLASSES).addClass(style.icon);
  }

  window.showFeedbackMessage = function (
    target,
    message,
    type = "info",
    options = {},
  ) {
    const $message = getMessageElement(target);

    if (!$message.length) {
      return;
    }

    const settings = $.extend(
      {
        autoHide: false,
        delay: 4000,
      },
      options,
    );

    clearHideTimer($message);
    applyStyle($message, type);

    $message.find(".feedback-message-text").text(message);
    $message.stop(true, true).hide().removeClass("hidden").fadeIn(180);

    if (settings.autoHide) {
      const timerId = window.setTimeout(function () {
        window.hideFeedbackMessage($message);
      }, settings.delay);

      $message.data("feedbackHideTimer", timerId);
    }
  };

  window.hideFeedbackMessage = function (target) {
    const $message = getMessageElement(target);

    if (!$message.length) {
      return;
    }

    clearHideTimer($message);

    $message.stop(true, true).fadeOut(180, function () {
      $message.addClass("hidden");
    });
  };

  $(document).on("click", "[data-feedback-close]", function () {
    window.hideFeedbackMessage($(this).closest("[data-feedback-message]"));
  });
})(jQuery);
