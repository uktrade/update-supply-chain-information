import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const urls = urlBuilder(supplyChain);

const scdInfoUrl = urls.scd + `${govDepartment.name}/` + `${supplyChain.fields.slug}/`

describe('The SCD info page', () => {
  it('successfully loads', () => {
    cy.visit(scdInfoUrl)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    // Due to header h1 and h3 with missing h2
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
    cy.get('h1.govuk-heading-xl').contains(`Supply chain details`)
    cy.get('p.govuk-body').contains('Detailed supply chain information')
    cy.get('h1.govuk-heading-xl').contains(supplyChain.fields.name)
    cy.get('span.govuk-caption-xl').contains(govDepartment.name)
  })
  it('displays navigation links', () => {
    cy.get('a.govuk-back-link')
      .contains('Back')
      .should('have.attr', 'href')
      .and('equal', '/chain-details/DIT/')

    cy.get('a').contains(
      'Back to top'
    )
  })

  it('expect summary info of supply chain', () => {
    cy.get('dl.govuk-summary-list div.govuk-summary-list__row--no-border')
      .should('have.length', 1)
      .each(($el, index) => {
        cy.wrap($el)
          .get('dd.govuk-summary-list__value h3.govuk-heading-s')
          .contains('Description')
          .should('not.have.attr', 'href')

        cy.wrap($el)
          .get('dd.govuk-summary-list__value')
          .contains(supplyChain.fields.description)
      })
  })
  it('shows the "Scenario testing" section', () => {
    cy.get('#supply-chain-scenario-testing')
      .should('have.length', 1)
      .each(($el) => {
        cy.wrap($el).find('summary').each(($el) => {
          cy.wrap($el).should('have.length', 1)
              .contains('Scenario testing')
        }).find('+ .govuk-details__text').each(($el) => {
          cy.wrap($el).should('have.length', 1)
            .find('> p')
            .contains('Useful information about how a supply chain might deal with a potential critical scenario.')
          cy.wrap($el).find('> h2').should('have.length', 1)
            .contains('Critical scenarios')
            .find('+ p').contains('Storage full: Bad things')
          cy.wrap($el).find('.govuk-accordion').each(($el) => {
            cy.wrap($el).should('have.length', 1)
              .find('> .govuk-accordion__section')
              .should('have.length', 6).each(($el) => {
                cy.wrap($el).find('> .govuk-accordion__section-header')
                  .should('have.length', 1)
                cy.wrap($el).find('> .govuk-accordion__section-content')
                    .should('have.length', 1)
            })
          })
        })
      })
  })
})
