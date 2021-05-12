Cypress.Commands.add(
    'monthlyUpdatePageHeader',
    {prevSubject: false,},
    () => {
        cy.govukMain().find('h1').contains('Strategic action monthly update')
    }
)

Cypress.Commands.add(
    'govukMain',
    {prevSubject: false,},
    () => {
        cy.get('main.govuk-main-wrapper')
    }
)

Cypress.Commands.add(
    'mainForm',
    {prevSubject: false,},
    () => {
        cy.govukMain().find('form')
    }
)

Cypress.Commands.add(
    'label',
    {
        prevSubject: true,
    },
    (subject) => {
        cy.wrap(subject).invoke('attr', 'id').then((fieldID) => {
            return cy.get(`label[for="${fieldID}"]`);
        })
    }
);

Cypress.Commands.add(
    'hasDjangoCSRFToken',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject)
                 .find('input[type="hidden"][name="csrfmiddlewaretoken"]')
                 .should('exist')
                 .invoke('val')
                 .should('not.be.empty');
    }
)

Cypress.Commands.add(
    'gdsFormGroup',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('govuk-form-group');
    }
)

Cypress.Commands.add(
    'gdsFormGroupError',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).gdsFormGroup().should('have.class', 'govuk-form-group--error');
    }
)

Cypress.Commands.add(
    'gdsErrorSummary',
    {
        prevSubject: false,
    },
    (subject) => {
        return cy.govukMain().find('div.govuk-error-summary:first-of-type').should('exist');
    }
)

Cypress.Commands.add(
    'noGdsErrorSummary',
    {
        prevSubject: false,
    },
    (subject) => {
        return cy.govukMain().find('div.govuk-error-summary:first-of-type').should('not.exist');
    }
)

Cypress.Commands.add(
    'gdsErrorList',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('.govuk-error-summary__list li a').should('exist');
    }
)

Cypress.Commands.add(
    'gdsFieldset',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('fieldset.govuk-fieldset').should('exist');
    }
)

Cypress.Commands.add(
    'submitButton',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('button[type="submit"]');
    }
)


Cypress.Commands.add(
    'hasSubmitButton',
    {
        prevSubject: true,
    },
    (subject, text='Save and continue') => {
        return cy.wrap(subject).submitButton().contains(text);
    }
)

Cypress.Commands.add(
    'hasCancelLink',
    {
        prevSubject: true,
    },
    (subject, cancelURL='') => {
        return cy.wrap(subject).find('a.govuk-button.govuk-button--secondary').should('exist').contains('Cancel').within((theCancelLink) => {
            cy.root().should('have.attr', 'href', `/${cancelURL}`)
        });
    }
)

Cypress.Commands.add(
    'summaryLists',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('dl.govuk-summary-list');
    }
)

Cypress.Commands.add(
    'summaryList',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('.govuk-summary-list__row');
    }
)

Cypress.Commands.add(
    'summaryListKey',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('dt.govuk-summary-list__key');
    }
)

Cypress.Commands.add(
    'summaryListValue',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('dd.govuk-summary-list__value');
    }
)

Cypress.Commands.add(
    'summaryListActions',
    {
        prevSubject: true,
    },
    (subject) => {
        return cy.wrap(subject).find('dd.govuk-summary-list__actions');
    }
)

Cypress.Commands.add(
    'govukLink',
    {
        prevSubject: true,
    },
    (subject, url) => {
        return cy.wrap(subject).find('a.govuk-link');
    }
)
Cypress.Commands.add(
    'summaryListChangeLink',
    {
        prevSubject: true,
    },
    (subject, url) => {
        return cy.wrap(subject).govukLink().contains('Change').invoke('attr', 'href', url);
    }
)

Cypress.Commands.add(
    'withFullText',
    {
        prevSubject: true,
    },
    (subject, expectedText) => {
        return cy.wrap(subject).invoke('text').then((text) => {
            expect(text).to.contain(expectedText);
        });
    }
)



