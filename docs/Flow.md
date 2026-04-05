
Click on search bar
  Typing "n" characters
    Show a list of "n" previewed results
    If n = 0
      End interaction
    Else
      Click on any Item showed in a list with preview "n" results
      Click on Search Icon
    Apply filters
      None
      Sort by 
        Price Low to High
        Price High or Low
      Price range
        Based on list of results. Get MAX and MIN and split in 5 slots
          S/. 0 - S/. 20
          S/. 21 - S/. 30
          ...
      Brands
        Based on list of results group by categories
          None
          Nike
          Adidas
    Click on "Apply Filters" button
      Show a list of "n" results
        If n = 0
          End interaction
        Else
          None
          Select (review) a product
          Save (like)
          Add Cart (Card)
            "n_items"+1
        If "n_items" = 0
          None
        Else
          None
          Remove item(s) of Cart (Card)
          Order
            Add Payment Method
              Digital Wallets (E-wallets)
              Credit & Debit Cards
              Buy Now, Pay Later (BNPL)
              Bank Transfers / ACHs
              Cryptocurrency
              Cash on Delivery (COD)
            Add address
              Confirm payment                                 
            Send an email that confirm payment
               Status
                 Pending
                 Confirmed
                 Shipped
                 Delivered