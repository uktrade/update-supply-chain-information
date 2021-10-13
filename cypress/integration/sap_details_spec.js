import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import actions from '../fixtures/strategicActions.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains.filter(sc => sc.fields.name === 'Supply Chain 1')[0]
const action = actions.filter(action => action.fields.name === 'SA 00')[0]
const urls = urlBuilder(supplyChain);

urls.sapDetail = urls.sap + `${govDepartment.name}/` + `${supplyChain.fields.slug}/` + `${action.fields.slug}/detail/`
urls.sapListing = `/action-progress/${govDepartment.name}/` + `${supplyChain.fields.slug}/`


describe('The SAP details page', () => {
  it('successfully loads', () => {
    cy.visit(urls.sapDetail)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y('html', {
      rules: {
        "heading-order": { enabled: false }
      }
    })
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Strategic action progress`)
    cy.get('p').contains('Strategic action progress details and information')
    cy.get('p').contains(`Apply filters to see strategic action progress`).should('not.exist')
    cy.get('h2.govuk-heading-l').contains(action.fields.name)
  })
  it('displays navigation links', () => {
    cy.get('a.govuk-back-link')
      .contains('Back')
      .should('have.attr', 'href')
      .and('equal', urls.sapListing)

    cy.get('a').contains(
      'Back to top'
    )
  })
  it('display summary table', () => {
    const summaryHeaders = ['Department', 'Supply chain', 'Strategic action status', 'Strategic action description', 'Start date', 'Estimated date of completion']
    const summaryValues = ['DIT', 'Supply Chain 1', 'Active', null, '6 Apr 2021']
    cy.get('#action-summary').should('exist')
    cy.get('#action-summary div.govuk-summary-list__row').should('have.length', 5)
    cy.get('#action-summary div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#action-summary div dd.govuk-summary-list__value')
      .should('have.length', 6)
      .each(($el, index) => {
        cy.wrap($el).find('h3.govuk-heading-s').contains(summaryHeaders[index])
        if (summaryValues[index]) {
          cy.wrap($el).contains(summaryValues[index])
        }
      })
  })
  it('display monthly update', () => {
    const updateHeaders = ['Latest monthly update', 'Delivery status', 'Last updated on']
    cy.get('#monthly-update').should('exist').should('not.have.attr', 'open')
    cy.get('#monthly-update summary.govuk-details__summary span.govuk-details__summary-text').contains('Monthly update')
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list').should('have.length', 1)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row').should('have.length', 2)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div dd.govuk-summary-list__value')
      .should('have.length', 3)
      .each(($el, index) => {
        if (index == 2) {
          cy.wrap($el).contains(updateHeaders[index])
        } else {
          cy.wrap($el).find('h3.govuk-heading-s').contains(updateHeaders[index])
        }
      })

    // NOTE: Commented due to GH #207
    // cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div dd.govuk-summary-list__value')
    //   .children(1).as('DeliveryStatus')
    // cy.get('@DeliveryStatus').contains('Amber')
    // cy.get('@DeliveryStatus')
    //   .find('details.govuk-details')
    //   .then(($ragDetail) => {
    //     cy.wrap($ragDetail).should('exist').should('not.have.attr', 'open')
    //     cy.wrap($ragDetail).find('summary.govuk-details__summary span.govuk-details__summary-text').contains('See more')
    //   })
  })
  it('display strategic action details', () => {
    cy.get('#action-details').should('exist').should('not.have.attr', 'open')
    cy.get('#action-details summary.govuk-details__summary span.govuk-details__summary-text').contains('Strategic action details')
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list').should('have.length', 1)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row').should('have.length', 6)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div dd.govuk-summary-list__value')
      .should('have.length', 7)
  })
  it('shows the QuickSight link', () => {
    cy.get('#app-quicksight-countries-link').should('exist')
    cy.get('#app-quicksight-countries-link a[href]').should('exist').should('contain.text', "Strategic action progress")
    cy.get('#app-quicksight-countries-link p.home-services-para').should('exist').should('contain.text', "Find out more about all strategic action progress and status history.")
  })
})

const archivedAction = actions.filter(action => action.fields.name == "SA 007")[0]
urls.sapDetailArchived = urls.sap + `${govDepartment.name}/` + `${supplyChain.fields.slug}/` + `${archivedAction.fields.slug}/detail/`

describe('The SAP details page for archived action', () => {
  it('successfully loads', () => {
    cy.visit(urls.sapDetailArchived)
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Strategic action progress`)
    cy.get('p').contains('Strategic action progress details and information')
    cy.get('p').contains(`Apply filters to see strategic action progress`).should('not.exist')
    cy.get('h2.govuk-heading-l').contains(archivedAction.fields.name)
  })
  it('displays navigation links', () => {
    cy.get('a.govuk-back-link')
      .contains('Back')
      .should('have.attr', 'href')
      .and('equal', urls.sapListing)

    cy.get('a').contains(
      'Back to top'
    )
  })
  it('display summary table', () => {
    const summaryHeaders = ['Department', 'Supply chain', 'Strategic action status', 'Strategic action description', 'Start date', 'Estimated date of completion', 'Archive date', 'Reason for archiving']
    const summaryValues = ['DIT', 'Supply Chain 1', 'Inactive', null, '1 Mar 2009', '31 Dec 2019', '1 Dec 2020', null]
    cy.get('#action-summary').should('exist')
    cy.get('#action-summary div.govuk-summary-list__row').should('have.length', 7)
    cy.get('#action-summary div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#action-summary div dd.govuk-summary-list__value')
      .each(($el, index) => {
        cy.wrap($el).find('h3.govuk-heading-s').contains(summaryHeaders[index])
        if (summaryValues[index]) {
          cy.wrap($el).contains(summaryValues[index])
        }
      })
  })
  it('display monthly update', () => {
    const updateHeaders = ['Latest monthly update', 'Delivery status', 'Last updated on']
    cy.get('#monthly-update').should('exist').should('not.have.attr', 'open')
    cy.get('#monthly-update summary.govuk-details__summary span.govuk-details__summary-text').contains('Monthly update')
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list').should('have.length', 1)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row').should('have.length', 2)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#monthly-update div.govuk-details__text dl.govuk-summary-list div dd.govuk-summary-list__value')
      .should('have.length', 3)
      .each(($el, index) => {
        if (index == 2) {
          cy.wrap($el).contains(updateHeaders[index])
        } else {
          cy.wrap($el).find('h3.govuk-heading-s').contains(updateHeaders[index])
        }
      })
  })
  it('display strategic action details', () => {
    cy.get('#action-details').should('exist').should('not.have.attr', 'open')
    cy.get('#action-details summary.govuk-details__summary span.govuk-details__summary-text').contains('Strategic action details')
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list').should('have.length', 1)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row').should('have.length', 6)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div.govuk-summary-list__row--no-border').should('have.length', 1)
    cy.get('#action-details div.govuk-details__text dl.govuk-summary-list div dd.govuk-summary-list__value')
      .should('have.length', 7)
  })
})
