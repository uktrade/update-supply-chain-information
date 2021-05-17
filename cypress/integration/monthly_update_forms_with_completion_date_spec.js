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
        'targetCompletionDate': action.fields.target_completion_date,
      };
    } else if (/^Has no update/.test(action.fields.description)) {
      const supplyChain = supplyChainsByPK[action.fields.supply_chain];
      if (/will be submitted with errors/.test(action.fields.description)) {
        accumulator.hasCompletionDate.forErrors = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
          'targetCompletionDate': action.fields.target_copmpletion_date,
        };
      } else {
        accumulator.hasCompletionDate.noUpdate = {
          'supplyChainSlug': supplyChain.fields.slug,
          'strategicActionSlug': action.fields.slug,
          'targetCompletionDate': action.fields.target_copmpletion_date,
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
    context('that does have a target completion date', function() {
      context('with an update from the previous month', function() {
        beforeEach(() => {
          Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
          cy.wrap(strategicActionsForTest.hasCompletionDate.hasUpdate).as('strategicAction')
          cy.wrap(urls.start(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('startURL')
          cy.wrap(urls.info(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('infoURL')
          cy.wrap(urls.timing(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('timingURL')
          cy.wrap(urls.status(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('statusURL')
          cy.wrap(urls.revisedtiming(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('revisedtimingURL')
          cy.wrap(urls.confirm(strategicActionsForTest.hasCompletionDate.hasUpdate)).as('confirmURL')
        });
        context('starting a new monthly update', () => {
          it('successfully creates a new update and redirects to its Update Info page', function() {
            cy.visit(this.startURL)
            cy.url().should('eq', this.infoURL)
            cy.injectAxe()
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
              it('the "Update information" link', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Action status" link', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Action status').should('exist')
              })
              it('the "Confirm" link', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Timing').should('not.exist')
                })
                it('the "Revised Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The link marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" link', () => {
                cy.get('@theBreadcrumbItems').eq(0).within(() => {
                  cy.root().get('a').should('have.attr', 'aria-current', 'page')
                })
              })
            })
          })
          context('The Update Info page content', function() {
            it('has the correct page header', () => {
              cy.monthlyUpdatePageHeader().should('exist')
            })
            it('shows the previous update', function() {
              cy.get('.app-dit-panel h2:first').contains('Last update')
              cy.get('.app-dit-panel h2:first + p').contains(this.strategicAction.updateContent)
            })
          })
          context('The Update Info form', () => {
            it('is there', () => {
              cy.mainForm().should('exist')
            })
            it('should have a CSRF token', () => {
              cy.mainForm().hasDjangoCSRFToken()
            })
            it('should have a textarea for the "content" field labelled "Latest monthly update"', () => {
              cy.mainForm().within((theForm) => {
                cy.get('textarea[name="content"]').label().should('contain.text', 'Latest monthly update')
              })
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.mainForm().hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.mainForm().hasCancelLink(`${this.strategicAction.supplyChainSlug}`)
            })
            context('When submitted with the content field filled out', function() {
              before(() => {
                // ensure we start with a clean slate
                cy.reload(true, {log: true})
              })
              it('should go to the "Action Status" page when saved', function() {
                cy.mainForm().within(function(theForm) {
                  cy.get('textarea[name="content"]').type(valuesToEnter.info.content)
                  cy.location('pathname').invoke('split', '/').its(5).as('strategicActionUpdateID')
                  cy.get('@strategicActionUpdateID').then(function(strategicActionUpdateID) {
                    cy.get('button[type="submit"]').click()
                    cy.url().should('eq', this.statusURL)
                    cy.injectAxe()
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
            context('The individual breadcrumbs in the ordered list should be', function() {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Update information" link', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Action status" link', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Action status').should('exist')
              })
              it('the "Confirm" link', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Timing').should('not.exist')
                })
                it('the "Revised Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Revised Timing').should('not.exist')
                })
              })
            })
            context('The link marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Delivery status" link', () => {
                cy.get('@theBreadcrumbItems').eq(1).within(() => {
                  cy.root().get('a').should('have.attr', 'aria-current', 'page')
                })
              })
            })
          })
          context('The Delivery Status page content', function() {
            it('has the correct page header', () => {
              cy.monthlyUpdatePageHeader().should('exist')
            })
            it ('shows the expected completion date', function() {
              cy.get('h1 ~ .govuk-inset-text > h2').contains("Current estimated date of completion").should('exist')
              cy.get('h1 ~ .govuk-inset-text > h2 + p').contains(targetCompletionDateAsString(this.strategicAction.targetCompletionDate)).should('exist')
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
              cy.mainForm().should('exist')
            })
            it('should have a CSRF token', () => {
              cy.mainForm().hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.mainForm().hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.mainForm().hasCancelLink(`${this.strategicAction.supplyChainSlug}`)
            })
            context('the radio buttons asking for the current delivery status', function() {
              beforeEach(() => {
                cy.mainForm().find('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item').as('theRadioItems')
                cy.get('@theRadioItems').children('input[type="radio"]').as('theRadioButtons')
                cy.get('@theRadioButtons').find('~ .govuk-hint').as('theRadioHints')
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
              context('Selecting the Green option', () => {
                it('and submitting the form should go to the "Check Your Answers" page', function() {
                  cy.get('@theRadioButtons').eq(0).click()
                  cy.mainForm().submitButton().click()
                  cy.url().should('eq', this.confirmURL)
                })
              })
              context('The "Amber" option', function() {
                beforeEach(() => {
                  cy.get('@theRadioButtons').eq(1).as('amberOption')
                })
                it('displays the potential risks textbox when selected', function() {
                  cy.get('@amberOption').click()
                  cy.get('@amberOption').invoke('attr', 'aria-controls').then((subjectID) => {
                    cy.get(`#${subjectID}`).should('be.visible')
                    cy.get(`#${subjectID}`).children(0).children('label').should('contain', 'Explain potential risk')
                    cy.get(`#${subjectID}`).children(0).children('textarea').should('be.visible')
                  })
                })
                context('and when completed', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(1).as('amberOption')
                    cy.get('@amberOption').click()
                    cy.get('@amberOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).children(0).children('textarea').type(valuesToEnter.status.options.Amber.reason)
                    })
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
                beforeEach(function() {
                  cy.visit(this.statusURL)
                  cy.get('@theRadioButtons').eq(2).as('redOption')
                })
                context('when selected', () => {
                  it('displays the Explain issue label and textbox', function() {
                    cy.get('@redOption').click()
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).should('be.visible')
                      cy.get(`#${subjectID}`).children(0).children('label').should('contain', 'Explain issue')
                      cy.get(`#${subjectID}`).children(0).children('textarea').should('be.visible')
                    })
                  })
                  it('displays the "Will the completion date change?" label and radios', function() {
                    cy.get('@redOption').click()
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID} > .govuk-form-group > fieldset > .govuk-radios > .govuk-radios__item`).as('dateChangeRadios')
                      cy.get(`#${subjectID}`).should('be.visible')
                      cy.get(`#${subjectID} > .govuk-form-group > fieldset > legend > h3`).should('contain', 'Will the estimated completion date change?')
                      cy.get('@dateChangeRadios').should('have.length', 2)
                      cy.get('@dateChangeRadios').eq(0).should('contain', 'Yes')
                      cy.get('@dateChangeRadios').eq(1).should('contain', 'No')
                    })
                  })
                })
                context('and when completed without specifying whether the completion date will change', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(2).as('redOption')
                    cy.get('@redOption').click()
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).children(0).children('textarea').type(valuesToEnter.status.options.Red.reason)
                    })
                  })
                  it('shows an error', function() {
                    cy.mainForm().submitButton().click()
                    cy.url().should('eq', this.statusURL)
                    cy.gdsErrorSummary().contains('Specify whether the estimated completion date will change').should('exist')
                    cy.mainForm().children('.govuk-form-group').should('have.class', 'govuk-form-group--error')
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).find('.govuk-form-group--error').contains('Specify whether the estimated completion date will change').should('exist')
                    })
                  })
                })
                context('and when completed specifying that the completion date WILL NOT change', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(2).as('redOption')
                    cy.get('@redOption').click()
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).children(0).children('textarea').type(valuesToEnter.status.options.Red.reason)
                    })
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).find('input[type="radio"]').as('yesNoRadios')
                      cy.get('@yesNoRadios').filter('[value="True"]').as('yesOption')
                      cy.get('@yesNoRadios').filter('[value="False"]').as('noOption')
                    })
                  })
                  it('saves the Red value and potential risks content when submitted', function() {
                    cy.get('@noOption').click()
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
                context('and when completed specifying that the completion date WILL change', () => {
                  beforeEach(() => {
                    cy.get('@theRadioButtons').eq(2).as('redOption')
                    cy.get('@redOption').click()
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).children(0).children('textarea').type(valuesToEnter.status.options.Red.reason)
                    })
                    cy.get('@redOption').invoke('attr', 'aria-controls').then((subjectID) => {
                      cy.get(`#${subjectID}`).find('input[type="radio"]').as('yesNoRadios')
                      cy.get('@yesNoRadios').filter('[value="True"]').as('yesOption')
                      cy.get('@yesNoRadios').filter('[value="False"]').as('noOption')
                    })
                  })
                  it('goes to the Revised Timing page when submitted', function() {
                    cy.get('@yesOption').click()
                    cy.mainForm().submitButton().click()
                    cy.url().should('eq', this.revisedtimingURL)
                  })
                })
              })
            })
          })
        })
        context('The Revised Timing page', function() {
          before(function() {
            // ensure the application state is such as to show the revised timing page
            cy.visit(this.statusURL)
            cy.mainForm().fieldLabelled('Red').click().revealedElement().within((revealedElement) => {
              cy.root().fieldLabelled('Explain issue').type(valuesToEnter.status.options.Red.reason)
              cy.root().fieldLabelled('Yes').click()
            })
            cy.mainForm().submitButton().click()
            cy.injectAxe()
          })
          it('has no accessibility issues', () => {
            cy.runA11y('html', {
              rules: {
                "aria-allowed-attr": { enabled: false }
              }
            })
          })
          context('The Revised Timing breadcrumbs', function() {
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
              it('the "Update information" link', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Action status" link', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Action status').should('exist')
              })
              it('the "Revised Timing" link', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Revised timing').should('exist')
              })
              it('the "Confirm" link', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Timing').should('not.exist')
                })
              })
            })
            context('The link marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Revised Timing" link', () => {
                cy.get('@theBreadcrumbItems').eq(2).within(() => {
                  cy.root().get('a').should('have.attr', 'aria-current', 'page')
                })
              })
            })
          })
          context('The Revised Timing page content', function() {
            it('has the correct page header', () => {
              cy.monthlyUpdatePageHeader().should('exist')
            })
            it ('shows the expected completion date', function() {
              cy.get('h1 ~ .govuk-inset-text > h2').contains("Current estimated date of completion").should('exist')
              cy.get('h1 ~ .govuk-inset-text > h2 + p').contains(targetCompletionDateAsString(this.strategicAction.targetCompletionDate)).should('exist')
            })
          })
          context('The Revised Timing form', () => {
            it('is there', () => {
              cy.mainForm().should('exist')
            })
            it('should have a CSRF token', () => {
              cy.mainForm().hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Save and continue"', () => {
              cy.mainForm().hasSubmitButton()
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.mainForm().hasCancelLink(`${this.strategicAction.supplyChainSlug}`)
            })
            it ('should have a fieldset with legend asking if the new completion date is known', () => {
              cy.mainForm().get('fieldset legend h2').contains('Do you know the revised expected completion date?').should('exist')
            })
            it ('should have a textarea with label asking the reason for the completion date change', () => {
              cy.mainForm().fieldLabelled('Reason for date change').should('exist').tagName().should('eq', 'textarea')
            })
            context('The radio buttons asking if the new completion date is known', function() {
              beforeEach(() => {
                cy.mainForm().get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
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
                  cy.mainForm().get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
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
                        cy.get('input').eq(0).should('have.attr', 'name', 'True-changed_target_completion_date_day')
                        cy.get('input').eq(0).invoke('attr', 'id').then((fieldID) => {
                          cy.get(`label[for="${fieldID}"]`).should('exist').contains('Day').should('exist')
                        })
                        cy.get('input').eq(1).should('have.attr', 'name', 'True-changed_target_completion_date_month')
                        cy.get('input').eq(1).invoke('attr', 'id').then((fieldID) => {
                          cy.get(`label[for="${fieldID}"]`).should('exist').contains('Month').should('exist')
                        })
                        cy.get('input').eq(2).should('have.attr', 'name', 'True-changed_target_completion_date_year')
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
                  // cy.mainForm().get('div.govuk-form-group > fieldset.govuk-fieldset > *[data-module="govuk-radios"] > .govuk-radios__item > input[type="radio"]').as('theRadioButtons')
                  // cy.get('@theRadioButtons').eq(0).as('theYesOption')
                  // cy.get('@theRadioButtons').eq(1).as('theNoOption')
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
                context('Selecting a duration, providing a reason and submitting the form', function() {
                  it('should go to the "Delivery status" page when saved', function() {
                    cy.mainForm().fieldLabelled('Reason for date change').type(valuesToEnter.revisedtiming.reason)
                    cy.get('@theNoOption').click()
                    cy.get('@theNoOption').invoke('attr', 'aria-controls').then(function(subjectID) {
                      /**
                       * The third radio button is "1 year", internally represented by the value 12
                       */
                      cy.get(`#${subjectID} input[type="radio"]`).eq(2).click()
                      cy.get('button[type="submit"]').click()
                      cy.url().should('eq', this.confirmURL)
                      cy.injectAxe()
                    })
                  })
                })
              })
            })
          })
        })
        context('The Check Your Answers page', function() {
          it('is there', function() {
            cy.visit(this.confirmURL)
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
              it('the "Update information" link', () => {
                cy.get('@theBreadcrumbItems').eq(0).contains('1. Update information').should('exist')
              })
              it('the "Action status" link', () => {
                cy.get('@theBreadcrumbItems').eq(1).contains('2. Action status').should('exist')
              })
              it('the "Revised Timing" link', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Revised timing').should('exist')
              })
              it('the "Confirm" link', () => {
                cy.get('@theBreadcrumbItems').eq(3).contains('4. Confirm').should('exist')
              })
              context('but should not include', () => {
                it('the "Timing" link', () => {
                  cy.get('@theBreadcrumbItems').contains('Timing').should('not.exist')
                })
              })
            })
            context('The link marked as the current page should be', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Confirm" link', () => {
                cy.get('@theBreadcrumbItems').eq(3).within(() => {
                  cy.root().get('a').should('have.attr', 'aria-current', 'page')
                })
              })
            })
          })
          context('The Check Your Answers page content should include', function() {
            it('the correct page header', () => {
              cy.monthlyUpdatePageHeader()
            })
            it('a medium-sized heading saying "Check your answers', () => {
              cy.govukMain().get('h2').should('have.class', 'govuk-heading-m').contains('Check your answers').should('exist')
            })
            it('a prompt to check the information', () => {
              cy.govukMain().get('h2 + p.govuk-body').contains("Check all the information you've provided is correct before submitting the form.").should('exist')
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
              context('the Delivery Status row', () => {
                beforeEach(() => {
                  cy.govukMain().summaryLists().eq(1).as('summary')
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
              context('the Revised Timing row', () => {
                beforeEach(() => {
                  cy.govukMain().summaryLists().eq(2).as('summary')
                })
                it('labelled "Estimated date of completion"', () => {
                  cy.get('@summary').summaryListKey().contains('Revised estimated date of completion').should('exist')
                })
                it('with the value entered on the "Timing" page', () => {
                  cy.get('@summary').summaryListValue().contains(targetCompletionDateRepresentation).should('exist')
                })
                context('and an actions column including', () => {
                  beforeEach(() => {
                    cy.get('@summary').summaryListActions().as('actions')
                  })
                  it('a "Change" link to the "Timing" page', () => {
                    cy.get('@actions').summaryListChangeLink(this.revisedtimingURL).should('exist')
                  })
                  it('with accessible text reading "Change revised estimated date of completion"', () => {
                    cy.get('@actions').govukLink().withFullText('Change revised estimated date of completion')
                  })
                })
              })
            })
          })
          context('Going back and saying the completion date will not change', () => {
            /**
             * This was causing a validation error,
             * as the question being treated as unanswered rather than answered in the negative
             * so check this  specifically
             */
            before(() => {
              cy.govukMain().summaryLists().eq(1).summaryListActions().summaryListChangeLink(this.statusURL).click()
              cy.mainForm().fieldLabelled('Red').click().revealedElement().within(() => {
                cy.root().fieldLabelled('No').click()
              })
              cy.mainForm().submitButton().click()
            })
            it('should now be back on the Check Your Answers page, not Revised Timing', function() {
              cy.url().should('eq', this.confirmURL)
              cy.url().should('not.eq', this.revisedtimingURL)
            })
            context('and should not have', () => {
              beforeEach(() => {
                cy.get('nav.moj-sub-navigation ol.moj-sub-navigation__list li').as('theBreadcrumbItems')
              })
              it('the "Revised Timing" link in the navigation', () => {
                cy.get('@theBreadcrumbItems').eq(2).contains('3. Revised Timing').should('not.exist')
              })
              it('or the Revised Timing row', () => {
                cy.govukMain().summaryLists().eq(2).should('not.exist')
              })
            })
          })
          context('The Check Your Answers form', () => {
            beforeEach(() => {
              cy.mainForm().as('theForm')
            })
            it('is there', () => {
              cy.get("@theForm").should('exist')
            })
            it('should have a CSRF token', () => {
              cy.get("@theForm").hasDjangoCSRFToken()
            })
            it('should have a submit button saying "Submit"', () => {
              cy.get('@theForm').hasSubmitButton('Submit')
            })
            it('should have a cancel link saying "Cancel" going back to the supply chain page', function() {
              cy.get('@theForm').hasCancelLink(`${this.strategicAction.supplyChainSlug}`)
            })
          })
        })
      })
    })
  })
})


// describe('Testing validation errors in the monthly update forms', () => {
//   context('for a strategic action', function() {
//       context('that does have a target completion date', function() {})
//   })
// })
