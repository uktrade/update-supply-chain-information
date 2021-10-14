import users from '../fixtures/user.json'
import govDepartments from '../fixtures/govDepartment.json'
import supplyChains from '../fixtures/supplyChains.json'
import { urlBuilder } from "../support/utils.js"

const adminUser = users[0].fields
const govDepartment = govDepartments[0].fields
const supplyChain = supplyChains[0]
const urls = urlBuilder(supplyChain);

const scdListingUrl = urls.scd + `${govDepartment.name}/`

describe('The SCD listing page', () => {
  it('successfully loads', () => {
    cy.visit(scdListingUrl)
    cy.injectAxe()
  })
  it('has no accessibility issues', () => {
    cy.runA11y()
  })
  it("displays user's name and department in header", () => {
    cy.get('.app-header-item').should(
      'have.text',
      `${adminUser.first_name} ${adminUser.last_name} - ${govDepartment.name}`
    )
  })
  it('displays the correct header', () => {
    cy.get('h1').contains(`Supply chain details`)
    cy.get('p').contains(`Filter supply chains by department`)
  })
  it('displays drop down for department', () => {
    cy.get('div > label').contains('Department')
    cy.get('div > label').find('Supply chain').should('not.exist')
    cy.get('div > select').should('have.length', 1)
  })
  it('displays enabled filter buttons', () => {
    cy.get('button').contains('Apply filters').should('be.enabled')
    cy.get('a').contains('Remove filters')
  })

  it('expect sections within filtered results', () => {
    const scs = supplyChains.sort((a,b) => (a.fields.name > b.fields.name) ? 1 : ((b.fields.name > a.fields.name) ? -1 : 0))
    const scNames = scs.slice(0, 5).map(sc => sc.fields.name)
    const scDescriptions = scs.slice(0, 5).map(sc => sc.fields.description)
    const scdInfoLinks = scs.slice(0, 5).map(sc => `/chain-details/${govDepartment.name}/${sc.fields.slug}/`)

    cy.get('h2').contains(`${govDepartment.name}`)
    cy.get('p').contains('Select a profile to view supply chain information')
    cy.get('a').contains(
      'Back to top'
    )
    cy.get('dl.govuk-summary-list div.govuk-summary-list__row')
      .should('have.length', 5)
      .each(($el, index) => {
        cy.wrap($el)
          .get('dd.govuk-summary-list__value a.govuk-link')
          .contains(scNames[index])
          .should('have.attr', 'href')
          .and('eq', scdInfoLinks[index])

        if (index == 3) {
          cy.wrap($el)
            .get('dd.govuk-summary-list__value p.scd-description')
            .contains(/.*.../)
        } else {
          cy.wrap($el)
            .get('dd.govuk-summary-list__value p.scd-description')
            .contains(scDescriptions[index])
        }
      })
  })
})


describe('Pagination of SCD list', () => {
  it('successfully loads', () => {
    cy.visit(scdListingUrl)
  })
  it('displays correct items in pagination list', () => {
    cy.get('.moj-pagination__list').find('li').should('have.length', 3)
    cy.get('.moj-pagination__item--active').contains('1')
    cy.get('.moj-pagination__item').contains('2')
    cy.get('.moj-pagination__item').contains('Next')
  })
  it('displays second page of supply chains after clicking Next', () => {
    cy.contains('Next').click()
    cy.url().should('eq', scdListingUrl + `?page=2`)
  })
  it('displays first page of supply chains after clicking Previous', () => {
    cy.contains('Previous').click()
    cy.url().should('eq', scdListingUrl + `?page=1`)
  })
})