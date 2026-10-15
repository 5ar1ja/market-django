# Products ER diagram

This diagram describes the products application.
Other applications are documented by their owners.

```mermaid
erDiagram
    Category {
        bigint id PK
        varchar title
        varchar slug UK
        bigint parent_id FK "nullable"
        boolean is_active
    }

    BRAND {
        bigint id PK
        varchar name
        varchar slug UK
        varchar logo "nullable"
    }

    PRODUCT {
        bigint id PK
        bigint category_id FK
        bigint brand_id FK "nullable"
        varchar title
        varchar slug UK
        varchar sku UK
        text description
        decimal price
        decimal old_price "nullable"
        integer stock
        boolean is_available
        datetime created_at
        datetime updated_at
    }

    PRODUCT_IMAGE {
        bigint id PK
        bigint product_id FK
        varchar image
        boolean is_main
        integer order
    }

    PRODUCT_ATTRIBUTE {
        bigint id PK
        varchar name
    }

    PRODUCT_ATTRIBUTE_VALUE {
        bigint id PK
        bigint product_id FK
        bigint attribute_id FK
        varchar value
    }

    CATEGORY o|--o{ CATEGORY : parent
    CATEGORY ||--o{ PRODUCT : contains
    BRAND o|--o{ PRODUCT :brands
    PRODUCT ||--o{ PRODUCT_IMAGE : images
    PRODUCT ||--o{ PRODUCT_ATTRIBUTE_VALUE : values
    PRODUCT_ATTRIBUTE ||--o{ PRODUCT_ATTRIBUTE_VALUE : describes
```
## Deletion rules

- Category.parent: CASCADE.
- Prodcut.category: PROTECT.
- Product.brand: SET_NULL.
- ProductImage.product: CASCADE.
- ProductAttributeValue.product: CASCADE.
- ProductAttributeValue.attribute: CASCADE.

Image fields store file paths in the database.