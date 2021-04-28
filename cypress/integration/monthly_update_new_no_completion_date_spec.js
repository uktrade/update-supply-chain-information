import supplyChains from '../fixtures/supplyChains.json'
import strategicActions from '../fixtures/strategicActions.json'
import strategicActionUpdates from '../fixtures/strategicActionUpdate.json'

const updatesByStrategicActionPK = strategicActionUpdates.reduce((accumulator, update) => {
  accumulator[update.fields.strategic_action] = update;
  return accumulator;
}, {});

const supplyChainsByPK = supplyChains.reduce((accumulator, supplyChain) => {
  accumulator[supplyChain.pk] = supplyChain;
  return accumulator;
}, {});

const strategicActionsForTest = strategicActions.reduce((accumulator, action) => {
  if (/a completion date/.test(action.fields.name)) {
    if (/^Has an update/.test(action.fields.name)) {
      const update = updatesByStrategicActionPK[action.pk],
        supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.hasCompletionDate.hasUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
        'updateSlug': update.fields.slug,
        'updatePK': update.pk,
      };
    } else if (/^Has no update/.test(action.fields.name)) {
      const supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.hasCompletionDate.noUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
      };
    }
  } else if (/no completion date/.test(action.fields.name)) {
    if (/^Has an update/.test(action.fields.name)) {
      const update = updatesByStrategicActionPK[action.pk],
          supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.noCompletionDate.hasUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
        'updateSlug': update.fields.slug,
      };
    } else if (/^Has no update/.test(action.fields.name)) {
      const supplyChain = supplyChainsByPK[action.fields.supply_chain];
      accumulator.noCompletionDate.noUpdate = {
        'supplyChainSlug': supplyChain.fields.slug,
        'strategicActionSlug': action.fields.slug,
      };
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

Cypress.Cookies.debug(true);

describe('Testing monthly update forms', () => {
  context('for a strategic action with a previous month update and no target completion date', () => {
    beforeEach(() => {
      Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
      cy.wrap(strategicActionsForTest.noCompletionDate.hasUpdate.supplyChainSlug).as('scSlug')
      cy.wrap(strategicActionsForTest.noCompletionDate.hasUpdate.strategicActionSlug).as('saSlug')
      cy.wrap(strategicActionsForTest.noCompletionDate.hasUpdate.updateSlug).as('uSlug')
    })
    it('successfully loads', function() {
      cy.visit(`http://localhost:8001/${this.scSlug}/strategic-actions/${this.saSlug}/update/start/`)
      cy.injectAxe()
    })
    context('The Info page', function() {
      it('has no accessibility issues', () => {
        cy.runA11y()
      })
      it('displays the correct page header', () => {
        cy.get('h1').contains(
            'Strategic action monthly update'
        )
      })
      it('displays the previous update', () => {
        cy.get('h2:first').contains('Last update')
        cy.get('h2:first + p').contains('submitted last month')
      })
      context('The Info form', function() {
        beforeEach(() => {
          cy.get('main form').as('theForm')
        })
        it('should exist', () => {
          cy.get("@theForm").should('exist')
        })
        it('should have a CSRF token', () => {
          cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').should('exist').invoke('val')
        })
        it('the CSRF token must not be empty', () => {
          cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').invoke('val').should('not.be.empty')
        })
        it ('should have a textarea for the "content" field', () => {
          cy.get("@theForm").within((theForm) => {
            cy.get('textarea[name="content"]').should('exist')
          })
        })
        it('should have a submit button saying "Save and continue"', () => {
          cy.get('@theForm').within((theForm) => {
            cy.get('button[type="submit"]').should('exist')
            cy.get('button[type="submit"]').contains('Save and continue')
          })
        })
        it ('should go to the "Timing" page when saved', function() {
          cy.get('@theForm').within((theForm) => {
            cy.location('pathname').invoke('split', '/').its(5).as('strategicActionUpdateID')
            cy.get('@strategicActionUpdateID').then(strategicActionUpdateID => {
              cy.get('button[type="submit"]').click()
              cy.url().should('eq', `http://localhost:8001/${this.scSlug}/strategic-actions/${this.saSlug}/update/${this.uSlug}/timing/`)
              cy.runA11y()
            })
          })
        })
      })
    })
  })
  // context('The Timing page', () => {
  //   beforeEach(() => {
  //     Cypress.Cookies.preserveOnce('csrftoken', 'sessionid')
  //   })
  //   it('has no accessibility issues', () => {
  //     cy.injectAxe()
  //   })
  //   it('displays the correct page header', () => {
  //     cy.get('h1').contains(
  //         'Strategic action monthly update'
  //
  //     )
  //   })
  //   // it('displays the previous update', () => {
  //   //   cy.get('h2:first').contains('Last update')
  //   //   cy.get('h2:first + p').contains('submitted last month')
  //   // })
  //   context('The Timing form', () => {
  //     beforeEach(() => {
  //       cy.get('main form').as('theForm')
  //     })
  //     it('should exist', () => {
  //       cy.get("@theForm").should('exist')
  //     })
  //     it('should have a CSRF token', () => {
  //       cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').should('exist').invoke('val')
  //     })
  //     it('the CSRF token must not be empty', () => {
  //       cy.get("@theForm").get('input[type="hidden"][name="csrfmiddlewaretoken"]').invoke('val').should('not.be.empty')
  //     })
  //   })
  // })
})
// http://localhost:8001/supply-chain-5/strategic-actions/strategic-action-0/update/04-2021/timing/