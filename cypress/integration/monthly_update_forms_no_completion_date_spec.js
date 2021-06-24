import supplyChains from '../fixtures/supplyChains.json'
import strategicActions from '../fixtures/strategicActions.json'
import strategicActionUpdates from '../fixtures/strategicActionUpdates.json'

const baseUrl = Cypress.config('baseUrl')

const updatesByStrategicActionPK = strategicActionUpdates.reduce((accumulator, update) => {
  accumulator[update.fields.strategic_action] = update;
  return accumulator;
}, {});

const supplyChainsByPK = supplyChains.reduce((accumulator, supplyChain) => {
  accumulator[supplyChain.pk] = supplyChain;
  return accumulator;
}, {});

const strategicActionsForTest = strategicActions.reduce((accumulator, action) => {
  if (/a completion date/.test(action.fields.description)) {
    if (/^Has an update/.test(action.fields.description)) {
      const update = updatesByStrategicActionPK[action.pk],
        supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.hasCompletionDate.hasUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
        'updateSlug': update.fields.slug,
        'updateContent': update.fields.content,
      };
    } else if (/^Has no update/.test(action.fields.description)) {
      const supplyChain = supplyChainsByPK[action.fields.supply_chain];
      if (/will be submitted with errors/.test(action.fields.description)) {
        accumulator.hasCompletionDate.forErrors = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
        };
      } else {
        accumulator.hasCompletionDate.noUpdate = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
        };
      }
    }
  } else if (/no completion date/.test(action.fields.description)) {
    if (/^Has an update/.test(action.fields.description)) {
      const update = updatesByStrategicActionPK[action.pk],
          supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.noCompletionDate.hasUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
        'updateSlug': update.fields.slug,
        'updateContent': update.fields.content,
        'name': action.fields.name
      };
    } else if (/^Has no update/.test(action.fields.description)) {
      const supplyChain = supplyChainsByPK[action.fields.supply_chain];
      if (/will be submitted with errors/.test(action.fields.description)) {
        accumulator.noCompletionDate.forErrors = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
        };
      } else {
        accumulator.noCompletionDate.noUpdate = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
        };
      }
    }
  }
  return accumulator;
}, {
  'hasCompletionDate': {
    'hasUpdate': [],
    'noUpdate': []
  },
  'noCompletionDate': {
    'hasUpdate': [],
    'noUpdate': []
  }
});

const today = new Date();
const isoToday = today.toISOString();
const todayMatches = /(\d{4})-(\d{2})/.exec(isoToday);
const todayMonth = todayMatches[2];
const todayYear = todayMatches[1];
const todaySlug = `${todayMonth}-${todayYear}`

const targetCompletionDate = new Date();
targetCompletionDate.setFullYear(today.getFullYear() + 1);

function targetCompletionDateAsString(isoTargetCompletionDate) {
  const targetCompletionDate = new Date(isoTargetCompletionDate);
  const targetCompletionDay = targetCompletionDate.toLocaleString('en-GB', {day: 'numeric'});
  const targetCompletionMonth = targetCompletionDate.toLocaleString('en-GB', {month: 'long'});
  const targetCompletionYear = targetCompletionDate.toLocaleString('en-GB', {year: 'numeric'});
  return `${targetCompletionDay} ${targetCompletionMonth} ${targetCompletionYear}`;
}
const targetCompletionDateRepresentation = targetCompletionDateAsString(targetCompletionDate);

const valuesToEnter = {
  info: {
    content: 'This is the text entered for the content field.'
  },
  timing: {
    Yes: {
      date: {
        day: 22,
        month: 11,
        year: 2023,
        monthString: 'November'
      },
    },
    No: {
      options: {
        durations: [
          [3, '3 months'],
          [6, '6 months'],
          [12, '1 year'],
          [24, '2 years'],
          [0, 'Ongoing'],
        ]
      }
    }
  },
  status: {
    options: {
      Red: {
        reason: 'This is the reason the status is RED',
        datechange: ['Yes', 'No']
      },
      Amber: {
        reason: 'This is the reason the status is AMBER',
      },
      Green: {
        lastUpdateValue: 'green',
      },
    }
  },
  revisedtiming: {
    yes: {
      date: {
        day: 22,
        month: 11,
        year: 2023,
      },
    },
    no: {
      options: {
        durations: [
          [3, '3 months'],
          [6, '6 months'],
          [12, '1 year'],
          [24, '2 years'],
          [0, 'Ongoing'],
        ]
      }
    },
    reason: 'This is the reason the completion date changed'
  },
}

const urls = {
  'start': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/start/`
  },
  'info': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/${todaySlug}/info/`
  },
  'timing': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/${todaySlug}/timing/`
  },
  'status': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/${todaySlug}/delivery-status/`
  },
  'revisedtiming': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/${todaySlug}/revised-timing/`
  },
  'confirm': function(strategicAction) {
    return `${baseUrl}/${strategicAction.supplyChainSlug}/${strategicAction.strategicActionSlug}/updates/${todaySlug}/confirm/`
  },
}

describe('Testing monthly update forms', () => {
  context('for a strategic action', function() {
    context('that has no target completion date', function() {
      context('with an update from the previous month', function() {
        beforeEach(function() {
          Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          cy.wrap(strategicActionsForTest.noCompletionDate.hasUpdate).as('strategicAction')
          cy.wrap(urls.start(strategicActionsForTest.noCompletionDate.hasUpdate)).as('startURL')
          cy.wrap(urls.info(strategicActionsForTest.noCompletionDate.hasUpdate)).as('infoURL')
          cy.wrap(urls.timing(strategicActionsForTest.noCompletionDate.hasUpdate)).as('timingURL')
          cy.wrap(urls.status(strategicActionsForTest.noCompletionDate.hasUpdate)).as('statusURL')
          cy.wrap(urls.confirm(strategicActionsForTest.noCompletionDate.hasUpdate)).as('confirmURL')
        });
        context('starting a new monthly update', function() {
          it('successfully creates a new update and redirects to its Update Info page', function() {
            cy.visit(this.startURL)
            cy.url().should('eq', this.infoURL)
          })
        })
        context('The Update Info page', function() {
          it('is there', function() {
            cy.visit(this.infoURL)
            cy.injectAxe()
          })
          it('has no accessibility issues', () => {
            cy.runA11y()
          })
          context('The Update Info breadcrumbs', function() {
            beforeEach(() => {
              cy.get('nav.moj-sub-navigation').as('theBreadcrumbs')
            })
            it('should be present', () => {
              cy.get('@theBreadcrumbs').should('exist')
            })
            it ('should contain an ordered list', () => {
              cy.get('@theBreadcrumbs').get('ol.moj-sub-navigation__list').should('exist')
            })
            context('The individual breadcrumbs in the ordered list should be', function() {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Timing').should('exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Action status').should('exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Revised Timing" item', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The breadcrumb marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).within(() => {
                  cy.root().find('span').should('have.attr', 'aria-current', 'page')
                })
              })
            })
            context('The breadcrumbs that are links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('none of them', () => {
                cy.get('@theBreadcrumbItems').find('a[href]').should('not.exist')
              })
            })
            context('The breadcrumbs that are not links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).find('a[href]').should('not.exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).find('a[href]').should('not.exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).find('a[href]').should('not.exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).find('a[href]').should('not.exist')
              })
            })
          })
          context('The Update Info page content', function() {
            it('has the correct page header', function() {
              cy.monthlyUpdatePageHeader(this.strategicAction.name).should('exist')
            })
            it('shows the previous update', function() {
              cy.get('.app-dit-panel h2:first').contains('Last update')
              cy.get('.app-dit-panel h2:first + p').contains(this.strategicAction.updateContent).should('exist')
            })
          })
          context('The Update Info form', () => {
            beforeEach(() => {
              cy.get('main form').as('theForm')
            })
            it('is there', () => {
              cy.get("@theForm").should('exist')
            })
            it('should have a CSRF token', () => {
              cy.get("@theForm").hasDjangoCSRFToken()
            })
            it('should have a textarea for the "content" field labelled "Latest monthly update"', () => {
              cy.get("@theForm").within((theForm) => {
                cy.get('textarea[name="content"]').label().should('contain.text', 'Latest monthly update')
              })
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.get('@theForm').hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.get('@theForm').hasCancelLink(`${this.strategicAction.supplyChainSlug}/`)
            })
            context('When submitted with the content field filled out', function() {
              before(() => {
                // ensure we start with a clean slate
                cy.reload(true, {log: true})
              })
              it('should go to the "Timing" page when saved', function() {
                cy.get('@theForm').within(function(theForm) {
                  cy.get('textarea[name="content"]').type(valuesToEnter.info.content)
                  cy.location('pathname').invoke('split', '/').its(5).as('strategicActionUpdateID')
                  cy.get('@strategicActionUpdateID').then(function(strategicActionUpdateID) {
                    cy.get('button[type="submit"]').click()
                    cy.url().should('eq', this.timingURL)
                    cy.injectAxe()
                  })
                })
              })
            })
          })
        })
        context('The Timing page', () => {
          beforeEach(() => {
            Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
            cy.mainForm().as('theForm')
          })
          it('is there', function() {
            cy.visit(this.timingURL)
            cy.injectAxe()
          })
          it('has no accessibility issues', () => {
            cy.runA11y('html', {
                rules: {
                  "aria-allowed-attr": { enabled: false }
                }
              })
          })
          context('The Timing breadcrumbs', function() {
            beforeEach(() => {
              cy.get('nav.moj-sub-navigation').as('theBreadcrumbs')
            })
            it ('should contain an ordered list', () => {
              cy.get('@theBreadcrumbs').get('ol.moj-sub-navigation__list').should('exist')
            })
            context('The individual breadcrumbs in the ordered list should be', function() {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Timing').should('exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Action status').should('exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Revised Timing" item', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The breadcrumb marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).within(() => {
                  cy.root().find('span').should('have.attr', 'aria-current', 'page')
                })
              })
            })
            context('The breadcrumbs that are links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).find('a[href]').should('exist')
              })
            })
            context('The breadcrumbs that are not links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).find('a[href]').should('not.exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).find('a[href]').should('not.exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).find('a[href]').should('not.exist')
              })
            })
          })
          context('The Timing page content', function() {
            it('has the correct page header', function() {
              cy.monthlyUpdatePageHeader(this.strategicAction.name).should('exist')
            })
            it ('warns that there is no expected completion date', () => {
              cy.get('h1 ~ .govuk-warning-text').contains("There's no expected completion date for this action.").should('exist')
            })
          })
          context('The Timing form', () => {
            it('is there', () => {
              cy.get("@theForm").should('exist')
            })
            it('should have a CSRF token', () => {
              cy.get("@theForm").hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.get('@theForm').hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.get('@theForm').hasCancelLink(`${this.strategicAction.supplyChainSlug}/`)
            })
            it ('should have a fieldset with legend asking if there is a completion date', () => {
              cy.get('@theForm').get('fieldset legend h2').contains('Is there an expected completion date?').should('exist')
            })
            context('The radio buttons asking if there is an expected completion date', function() {
              beforeEach(() => {
                cy.get('@theForm').get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
              })
              it('should be present', () => {
                cy.get('@theRadioButtons').should('exist')
              })
              it('should be two in number', () => {
                cy.get('@theRadioButtons').should('have.length', 2)
              })
              it('the first should have the label "Yes"', () => {
                cy.get('@theRadioButtons').eq(0).siblings('label').eq(0).contains('Yes').should('exist')
              })
              it('the second should have the label "No"', () => {
                cy.get('@theRadioButtons').eq(1).siblings('label').eq(0).contains('No').should('exist')
              })
              context('The "Yes" option', function() {
                before(() => {
                  // ensure we start with a clean slate
                  cy.reload(true, {log: true})
                })
                beforeEach(() => {
                  cy.get('@theForm').get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
                  cy.get('@theRadioButtons').eq(0).as('theYesOption')
                  cy.get('@theRadioButtons').eq(1).as('theNoOption')
                })
                it('should initially be unchecked', () => {
                  cy.get('@theYesOption').should('not.be.checked')
                })
                it('its subject should initially be hidden', () => {
                  cy.get('@theYesOption').invoke('attr', 'aria-controls').then((subjectID) => {
                    cy.get(`#${subjectID}`).should('be.hidden')
                  })
                })
                context('When it is selected, it', function() {
                  it('should make the date entry fields visible', () => {
                    cy.get('@theYesOption').click()
                    cy.get('@theYesOption').revealedElement().should('be.visible')
                  })
                  it('the approximate timing or ongoing fields should remain hidden', () => {
                    cy.get('@theNoOption').revealedElement().should('be.hidden')
                  })
                  context('The revealed date entry fields', function() {
                    beforeEach(() => {
                      cy.get('@theYesOption').revealedElement().as('theDateSection')
                    })
                    it ('should have all its date fields and labels for day, month, and year', () => {
                      cy.get('@theDateSection').within(() => {
                        cy.get('input').eq(0).should('have.attr', 'name', 'True-changed_value_for_target_completion_date_day')
                        cy.get('input').eq(0).invoke('attr', 'id').then((fieldID) => {
                          cy.get(`label[for="${fieldID}"]`).should('exist').contains('Day').should('exist')
                        })
                        cy.get('input').eq(1).should('have.attr', 'name', 'True-changed_value_for_target_completion_date_month')
                        cy.get('input').eq(1).invoke('attr', 'id').then((fieldID) => {
                          cy.get(`label[for="${fieldID}"]`).should('exist').contains('Month').should('exist')
                        })
                        cy.get('input').eq(2).should('have.attr', 'name', 'True-changed_value_for_target_completion_date_year')
                        cy.get('input').eq(2).invoke('attr', 'id').then((fieldID) => {
                          cy.get(`label[for="${fieldID}"]`).should('exist').contains('Year').should('exist')
                        })
                      })
                    })
                  })
                })
              })
              context('The "No" option', function() {
                before(() => {
                  // ensure we start with a clean slate
                  cy.reload(true, {log: true})
                })
                beforeEach(() => {
                  cy.mainForm().fieldLabelled('Yes').as('theYesOption')
                  cy.mainForm().fieldLabelled('No').as('theNoOption')
                })
                it('should initially be unchecked', () => {
                  cy.get('@theNoOption').should('not.be.checked')
                })
                it('its subject should initially be hidden', () => {
                  cy.get('@theNoOption').revealedElement().within((subjectID) => {
                    cy.root().should('exist')
                    cy.root().should('be.hidden')
                  })
                })
                context('When it is selected, it', function() {
                  it('should make the approximate timing or ongoing fields visible', () => {
                    cy.get('@theNoOption').click()
                    cy.get('@theNoOption').revealedElement().should('be.visible')
                  })
                  it('the date entry fields should remain hidden', () => {
                    cy.get('@theYesOption').revealedElement().should('be.hidden')
                  })
                  context('The revealed approximate timing or ongoing fields', function() {
                    beforeEach(() => {
                      cy.get('@theNoOption').revealedElement().as('theApproximateTimingSection')
                      cy.wrap(valuesToEnter.timing.No.options.durations).as('approximateTimings')
                    })
                    it('should have radio buttons and labels for 3 months to 2 years or Ongoing', () => {
                      cy.get('@theApproximateTimingSection').within(() => {
                        cy.get('@approximateTimings').then((approximateTimings) => {
                          approximateTimings.forEach((approximateTiming, index) => {
                            cy.get('input').eq(index).should('have.attr', 'name', 'False-surrogate_is_ongoing')
                            cy.get('input').eq(index).should('have.attr', 'value', approximateTiming[0]).invoke('attr', 'id').then((fieldID) => {
                              cy.get(`label[for="${fieldID}"]`).contains(approximateTiming[1]).should('exist')
                            })
                          })
                        })
                      })
                    })
                  })
                })
                context('Selecting a duration and submitting the form', function() {
                  it('should go to the "Delivery status" page when saved', function() {
                    cy.get('@theNoOption').click()
                    cy.get('@theNoOption').invoke('attr', 'aria-controls').then(function(subjectID) {
                      /**
                       * The third radio button is "1 year", internally represented by the value 12
                       */
                      cy.get(`#${subjectID} input[type="radio"]`).eq(2).click()
                      cy.get('button[type="submit"]').click()
                      cy.url().should('eq', this.statusURL)
                      cy.injectAxe()
                    })
                  })
                })
              })
            })
          })
        })
        context('The Delivery Status page', () => {
          beforeEach(() => {
            Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          })
          it('is there', function() {
            cy.visit(this.statusURL)
            cy.injectAxe()
          })
          it('has no accessibility issues', () => {
            cy.runA11y('html', {
              rules: {
                "aria-allowed-attr": { enabled: false }
              }
            })
          })
          context('The Delivery Status breadcrumbs', function() {
            beforeEach(() => {
              cy.get('nav.moj-sub-navigation').as('theBreadcrumbs')
            })
            it ('should contain an ordered list', () => {
              cy.get('@theBreadcrumbs').get('ol.moj-sub-navigation__list').should('exist')
            })
            context('The individual breadcrumbs in the ordered list should be', function() {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Timing').should('exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Action status').should('exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Revised Timing" item', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The breadcrumb marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Delivery status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).within(() => {
                  cy.root().find('span').should('have.attr', 'aria-current', 'page')
                })
              })
            })
            context('The breadcrumbs that are links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).find('a[href]').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).find('a[href]').should('exist')
              })
            })
            context('The breadcrumbs that are not links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).find('a[href]').should('not.exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).find('a[href]').should('not.exist')
              })
            })
          })
          context('The Delivery Status page content', function() {
            it('has the correct page header', function() {
              cy.monthlyUpdatePageHeader(this.strategicAction.name).should('exist')
            })
            it ('shows the "Adjusted" completion date just specified on the Timing page', function() {
              cy.get('h1 ~ .govuk-inset-text > h2').contains("Adjusted estimated date of completion").should('exist')
              cy.get('h1 ~ .govuk-inset-text > h2 + p').contains(targetCompletionDateRepresentation).should('exist')
            })
            it ('shows instructions', () => {
              cy.mainForm().find('legend + .govuk-body > p:first-of-type').contains('When considering if delivery of the strategic action is on track, consider:');
              ['costs', 'timings', 'quality'].forEach((itemText, i) => {
                cy.mainForm().find('legend + .govuk-body > ul > li').eq(i).contains(itemText).should('exist')
              })
            })
            it('shows the delivery status for the previous month', function() {
              cy.mainForm().find('legend + .govuk-body > p:last-of-type').contains(`Your last status update was ${valuesToEnter.status.options.Green.lastUpdateValue}`).should('exist')
            })
          })
          context('The Delivery Status form', () => {
            beforeEach(function() {
              cy.visit(this.statusURL)
              cy.mainForm().as('theForm')
            })
            it('is there', () => {
              cy.get("@theForm").should('exist')
            })
            it('should have a CSRF token', () => {
              cy.get("@theForm").hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.get('@theForm').hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.get('@theForm').hasCancelLink(`${this.strategicAction.supplyChainSlug}/`)
            })
            context('the radio buttons asking for the current delivery status', function() {
              beforeEach(() => {
                cy.get('@theForm').get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item').as('theRadioItems')
                cy.get('@theRadioItems').get('input[type="radio"]').as('theRadioButtons')
                cy.get('@theRadioButtons').get('.govuk-hint').as('theRadioHints')
              })
              it('should be three in number', () => {
                cy.get('@theRadioButtons').should('have.length', 3)
                cy.get('@theRadioHints').should('have.length', 3)
              })
              it('the first should have the label "Green" and the correct hint text', () => {
                cy.get('@theRadioButtons').eq(0).siblings('label').eq(0).contains('Green').should('exist')
                cy.get('@theRadioHints').eq(0).contains('Delivery is on track with no issues').should('exist')
              })
              it('the second should have the label "Amber" and the correct hint text', () => {
                cy.get('@theRadioButtons').eq(1).siblings('label').eq(0).contains('Amber').should('exist')
                cy.get('@theRadioHints').eq(1).contains("There's a potential risk to delivery that needs monitoring.").should('exist')
              })
              it('the third should have the label "Red" and the correct hint text', () => {
                cy.get('@theRadioButtons').eq(2).siblings('label').eq(0).contains('Red').should('exist')
                cy.get('@theRadioHints').eq(2).contains("There is an issue with delivery of an action. This will require escalation and further support. There is a potential risk to the expected completion date.").should('exist')
              })
              context('The "Amber" option', function() {
                beforeEach(() => {
                  cy.get('@theRadioButtons').eq(1).as('amberOption')
                })
                it('displays the potential risks textbox when selected', function() {
                  cy.get('@amberOption').click()
                  cy.get('@amberOption').revealedElement().within((revealedElement) => {
                    cy.root().should('be.visible')
                    cy.root().children(0).children('label').should('contain', 'Explain potential risk')
                    cy.root().children(0).children('textarea').should('be.visible')
                  })
                })
                context('and when completed', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(1).as('amberOption')
                    cy.get('@amberOption').click()
                    cy.get('@amberOption').revealedElement().children(0).children('textarea').type(valuesToEnter.status.options.Amber.reason)
                  })
                  it('saves the Amber value and potential risks content when submitted', function() {
                    cy.mainForm().submitButton().click()
                    cy.url().should('eq', this.confirmURL)
                  })
                  context('and the Check Answers page', () => {
                    beforeEach(function() {
                      cy.visit(this.confirmURL)
                    })
                    it('shows the saved values', function() {
                      cy.govukMain().summaryLists().summaryListValue().contains('Amber').should('exist')
                      cy.govukMain().summaryLists().summaryListValue().contains(valuesToEnter.status.options.Amber.reason).should('exist')
                    })
                  })
                })
              })
              context('The "Red" option', function() {
                beforeEach(() => {
                  cy.get('@theRadioButtons').eq(2).as('redOption')
                })
                it('displays the Explain issue label and textbox when selected', function() {
                  cy.get('@redOption').click()
                  cy.get('@redOption').revealedElement().within((revealedElement) => {
                      cy.root().should('be.visible')
                      cy.root().children(0).children('label').should('contain', 'Explain issue')
                      cy.root().children(0).children('textarea').should('be.visible')
                    })
                })
                context('and when completed', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(2).as('redOption')
                    cy.get('@redOption').click()
                    cy.get('@redOption').revealedElement().children(0).children('textarea').type(valuesToEnter.status.options.Red.reason)
                  })
                  it('saves the Red value and potential risks content when submitted', function() {
                    cy.mainForm().submitButton().click()
                    cy.url().should('eq', this.confirmURL)
                  })
                  context('and the Check Answers page', () => {
                    beforeEach(function() {
                      cy.visit(this.confirmURL)
                    })
                    it('shows the saved values', function() {
                      cy.govukMain().summaryLists().summaryListValue().contains('Red').should('exist')
                      cy.govukMain().summaryLists().summaryListValue().contains(valuesToEnter.status.options.Red.reason).should('exist')
                    })
                  })
                })
              })
              it('Selecting the "Green" option and submitting the form should go to the "Check Your Answers" page', function() {
                cy.get('@theRadioButtons').eq(0).click()
                cy.get('@theForm').submitButton().click()
                cy.url().should('eq', this.confirmURL)
              })
            })
          })
          context('Returning to the "Timing" page and selecting Ongoing then coming back to "Delivery Status"', function() {
            beforeEach(function() {
              cy.visit(this.timingURL)
              cy.mainForm().fieldLabelled('No').click()
              cy.mainForm().fieldLabelled('Ongoing').click()
              cy.mainForm().submitButton().click()
            })
            it ('shows the "Adjusted" timing as "Ongoing"', function() {
              cy.get('h1 ~ .govuk-inset-text > h2').contains("Adjusted estimated date of completion").should('exist')
              cy.get('h1 ~ .govuk-inset-text > h2 + p').contains('Ongoing').should('exist')
            })
          })
        })
        context('The Check Your Answers page', () => {
          beforeEach(() => {
            Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          })
          it('is there', function() {
            cy.visit(this.confirmURL)
            cy.injectAxe()
          })
          it('has no accessibility issues', () => {
            cy.runA11y()
          })
          context('The Check Your Answers breadcrumbs', function() {
            beforeEach(() => {
              cy.get('nav.moj-sub-navigation').as('theBreadcrumbs')
            })
            it ('should contain an ordered list', () => {
              cy.get('@theBreadcrumbs').get('ol.moj-sub-navigation__list').should('exist')
            })
            context('The individual breadcrumbs in the ordered list should be', function() {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Timing').should('exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Action status').should('exist')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Revised Timing" item', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The breadcrumb marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).within(() => {
                  cy.root().find('span').should('have.attr', 'aria-current', 'page')
                })
              })
            })
            context('The breadcrumbs that are links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" item', () => {
                cy.get('@theBreadcrumbItems').eq(0).find('a[href]').should('exist')
              })
              it('the "Timing" item', () => {
                cy.get('@theBreadcrumbItems').eq(1).find('a[href]').should('exist')
              })
              it('the "Action status" item', () => {
                cy.get('@theBreadcrumbItems').eq(2).find('a[href]').should('exist')
              })
            })
            context('The breadcrumbs that are not links should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Confirm" item', () => {
                cy.get('@theBreadcrumbItems').eq(3).find('a[href]').should('not.exist')
              })
            })
          })
          context('The Check Your Answers page content should include', function() {
            it('the correct page header', function() {
              cy.monthlyUpdatePageHeader(this.strategicAction.name)
            })
            it('a medium-sized heading saying "Check your answers', () => {
              cy.govukMain().get('h2').should('have.class', 'govuk-heading-m').contains('Check your answers').should('exist')
            })
            it('a prompt to check the information', () => {
              cy.govukMain().get('h2 + p.govuk-body').contains("Check all the information you've provided is correct before confirming.").should('exist')
            })
            it('shouldn\'t have an error summary', function() {
              cy.noGdsErrorSummary()
            })
            it('should have summary lists', () => {
              cy.govukMain().summaryLists().should('exist')
            })
            context('The summary lists should include', function() {
              describe('the Info row', () => {
                beforeEach(() => {
                  cy.govukMain().summaryLists().eq(0).as('summary')
                })
                it('labelled "Latest monthly update"', () => {
                  cy.get('@summary').summaryListKey().contains('Latest monthly update').should('exist')
                })
                it('with the value entered on the "Info" page', () => {
                  cy.get('@summary').summaryListValue().contains(valuesToEnter.info.content).should('exist')
                })
                context('and an actions column including', () => {
                  beforeEach(() => {
                    cy.get('@summary').summaryListActions().as('actions')
                  })
                  it('a "Change" link to the "Info" page', () => {
                    cy.get('@actions').summaryListChangeLink(this.infoURL).should('exist')
                  })
                  it('with accessible text reading "Change latest monthly update"', () => {
                    cy.get('@actions').govukLink().withFullText('Change latest monthly update')
                  })
                })
              })
              context('the Timing row', () => {
                beforeEach(function() {
                  // tidy up timing so the expected conditions are met
                  cy.visit(this.timingURL)
                  cy.mainForm().fieldLabelled('No').click()
                  cy.mainForm().fieldLabelled('1 year').click()
                  cy.mainForm().submitButton().click()
                  cy.visit(this.confirmURL)
                  cy.govukMain().summaryLists().eq(1).as('summary')
                })
                it('labelled "Estimated date of completion"', () => {
                  cy.get('@summary').summaryListKey().contains('Estimated date of completion').should('exist')
                })
                it('with the value entered on the "Timing" page', () => {
                  cy.get('@summary').summaryListValue().contains(targetCompletionDateRepresentation).should('exist')
                })
                context('and an actions column including', () => {
                  beforeEach(() => {
                    cy.get('@summary').summaryListActions().as('actions')
                  })
                  it('a "Change" link to the "Timing" page', () => {
                    cy.get('@actions').summaryListChangeLink(this.timingURL).should('exist')
                  })
                  it('with accessible text reading "Change estimated date of completion"', () => {
                    cy.get('@actions').govukLink().withFullText('Change estimated date of completion')
                  })
                })
              })
              describe('the Delivery Status row', () => {
                beforeEach(() => {
                  cy.govukMain().summaryLists().eq(2).as('summary')
                })
                it('labelled "Current delivery status"', () => {
                  cy.get('@summary').summaryListKey().contains('Current delivery status').should('exist')
                })
                it('with the value entered on the "Delivery Status" page', () => {
                  // cy.get('@summary').summaryListValue().contains(valuesToEnter.info.content)
                })
                context('and an actions column including', () => {
                  beforeEach(() => {
                    cy.get('@summary').summaryListActions().as('actions')
                  })
                  it('a "Change" link to the "Info" page', () => {
                    cy.get('@actions').summaryListChangeLink(this.statusURL).should('exist')
                  })
                  it('with accessible text reading "Change current delivery status"', () => {
                    cy.get('@actions').govukLink().withFullText('Change current delivery status')
                  })
                })
              })
            })
          })
          context('The Check Your Answers form', () => {
            beforeEach(() => {
              cy.get('main form').as('theForm')
            })
            it('is there', () => {
              cy.get("@theForm").should('exist')
            })
            it('should have a CSRF token', () => {
              cy.get("@theForm").hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Confirm"', () => {
              cy.get('@theForm').hasSubmitButton('Confirm')
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.get('@theForm').hasCancelLink(`${this.strategicAction.supplyChainSlug}/`)
            })
          })
          context('Following the Timing row "Change" link and changing the selection to "Ongoing"', () => {
            before(() => {
              cy.govukMain().summaryLists().eq(1).summaryListActions().govukLink().click()
              cy.mainForm().get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
              cy.get('@theRadioButtons').eq(1).as('theNoOption')
              cy.get('@theNoOption').click()
              cy.get('@theNoOption').invoke('attr', 'aria-controls').then(function(subjectID) {
                /**
                 * The fifth radio button is "Ongoing", internally represented by the value 0
                 */
                cy.get(`#${subjectID} input[type="radio"]`).eq(4).click()
                cy.mainForm().submitButton().click()
              })
            })
            beforeEach(() => {
              cy.get('@confirmURL').then((url) => {
                cy.visit(url)
              })
              cy.govukMain().summaryLists().eq(1).as('timingRow')
            })
            it('should show that the "Timing" section value is now "Ongoing"', () => {
              cy.get('@timingRow').summaryListValue().contains("Ongoing").should('exist')
            })
          })
        })
      })
      context('without an update from the previous month', function() {
        beforeEach(() => {
          Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          cy.wrap(strategicActionsForTest.noCompletionDate.noUpdate).as('strategicAction')
          cy.wrap(urls.start(strategicActionsForTest.noCompletionDate.noUpdate)).as('startURL')
          cy.wrap(urls.info(strategicActionsForTest.noCompletionDate.noUpdate)).as('infoURL')
          cy.wrap(urls.timing(strategicActionsForTest.noCompletionDate.noUpdate)).as('timingURL')
          cy.wrap(urls.confirm(strategicActionsForTest.noCompletionDate.noUpdate)).as('confirmURL')
          cy.wrap(todaySlug).as('todaySlug')
        });
        context('starting a new monthly update', function() {
          it('successfully creates a new update and redirects to its Update Info page', function() {
            cy.visit(this.startURL)
            cy.url().should('eq', this.infoURL)
            cy.injectAxe()
          })
        })
        context('The Update Info page', function() {
          it('has no accessibility issues', () => {
            cy.runA11y()
          })
          context('The Update Info page content', function() {
            it('does not include a previous update', function() {
              cy.get('.app-dit-panel').should('not.exist')
            })
          })
        })
      })
    })
  })
})



const expectedErrors = {
  info: {
    content: {
      required: 'Enter details of the latest monthly update'
    },
  },
  timing: {
    required: 'Specify whether the date for intended completion is known',
    Yes: {
      required: 'Enter a date for intended completion',
      invalid: 'Enter a date for intended completion in the correct format',
    },
    No: {
      required: 'Select an approximate time for completion',
      invalid_choice: 'Select an approximate time for completion',
    },
  },
  status: {
    required: 'Select an option for the current delivery status',
    invalid_choice: 'Select a valid option for the current delivery status',
    Red: {
      will_completion_date_change: {
        required: 'Specify whether the estimated completion date will change',
        invalid_choice: 'Specify whether the estimated completion date will change',
      },
      reason_for_delays: {
        required: "Enter an explanation of the issue",
      }
    },
    Amber: {
      reason_for_delays: {
        required: "Enter an explanation of the potential risk",
      }
    },
  },
}

describe('Testing validation errors in the monthly update forms', () => {
  context('for a strategic action', function() {
    context('that has no target completion date', function() {
        beforeEach(() => {
          Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          cy.wrap(strategicActionsForTest.noCompletionDate.forErrors).as('strategicAction')
          cy.wrap(urls.start(strategicActionsForTest.noCompletionDate.forErrors)).as('startURL')
          cy.wrap(urls.info(strategicActionsForTest.noCompletionDate.forErrors)).as('infoURL')
          cy.wrap(urls.timing(strategicActionsForTest.noCompletionDate.forErrors)).as('timingURL')
          cy.wrap(urls.confirm(strategicActionsForTest.noCompletionDate.forErrors)).as('confirmURL')
        });
        it ('starts a new update', function() {
          cy.visit(this.startURL)
        })
        context('The Check Your Answers page', () => {
          before(function() {
            cy.visit(this.confirmURL)
          })
          beforeEach(() => {
            Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
            cy.gdsErrorSummary().as('errors')
          })
          it('shows an error for the Info page', () => {
            cy.get('@errors').contains(expectedErrors.info.content.required).should('exist')
          })
          it('shows an error for the Timing page', () => {
            cy.get('@errors').contains(expectedErrors.timing.required).should('exist')
          })
          it('shows an error for the Delivery Status page', () => {
            cy.get('@errors').contains(expectedErrors.status.required).should('exist')
          })
        })
      })
  })
})
