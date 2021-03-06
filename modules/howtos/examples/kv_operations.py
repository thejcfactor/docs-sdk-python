"""
= Key Value Operations
:navtitle: KV Operations
:page-topic-type: howto
:page-aliases: document-operations.adoc

WARNING: These pages cover the first _Developer Preview_ of the Couchbase .NET SDK 3.0 (DP1).
As such they are likely to change without notice.
The DP1 code _should not_ be used in production.


The complete code sample used on this page can be downloaded from
//  xref::example$document.cs[here]
- from which you can see in context how to authenticate and connect to a Couchbase Cluster, then perform these Bucket operations.

// Type hints!
// Type hints!
// Type hints!
// Type hints!
// Type hints!
//
//    :-)

== Documents

A _document_ refers to an entry in the database (other databases may refer to the same concept as a _row_).
A document has an ID (_primary key_ in other databases), which is unique to the document and by which it can be located.
    The document also has a value which contains the actual application data.
    See xref::concept-docs:documents.adoc[the concept guide to _Documents_] for a deeper dive into documents in the Couchbase Data Platform.
Or read on, for a hands-on introduction to working with documents from the .NET SDK.

== CRUD Operations

The core interface to Couchbase Server is simple KV operations on full documents.
Make sure you're familiar with the basics of authorization and connecting to a Cluster from the xref::hello-world:start-using-sdk.adoc[Start Using the SDK section].
We're going to expand on the short _Upsert_ example we used there, adding options as we move through the various CRUD operations.
Here is the _Insert_ operation at its simplest:

    [source,python]
    ----
    Insert
"""
import couchbase.cluster
from couchbase.collection import DeltaValue, SignedInt64, RemoveOptions
cluster=couchbase.cluster.Cluster("fred")
cb=cluster.bucket("keith")
collection=cb.default_collection()

#tag::insert[]
document = {"foo":"bar", "bar":"foo"}
result = collection.insert("document-key", document)
#end::insert[]
"""         ----

Options may be added to operations:

[source,python]
----
Insert (with options)
"""
#tag::insert_w_options[]
from couchbase.durability import ClientDurability, ServerDurability, Durability, ReplicateTo, PersistTo
from datetime import timedelta
document = {"foo":"bar", "bar":"foo"}
result = collection.insert("document-key", document, expiry=timedelta(seconds=5))
#end::insert_w_options[]
"""----

Setting a Compare and Swap (CAS) value is a form of optimistic locking - dealt with in depth in the xref:concurrent-document-mutations.adoc[CAS page].
Here we just note that the CAS is a value representing the current state of an item; each time the item is modified, its CAS changes.
    The CAS value is returned as part of a document’s metadata whenever a document is accessed.
    Without explicitly setting it, a newly-created document would have a CAS value of _0_.

                                                                                          _Timeout_ is an optional parameter which in the .NET SDK has a type value of `TimeSpan`.
    Timeout sets the timeout value for the underlying network connection.
We will add to these options for the _Replace_ example:

    [source,python]
    ----
"""
#tag::replace[]
document = {"foo":"bar","bar":"foo"}
result = collection.replace("document-key", document, cas = 12345, expiry = timedelta(minutes=1))
#end::replace[]
"""
----

Expiration sets an explicit time to live (TTL) for a document, for which you can also xref:sdk-xattr-example.adoc[see a more detailed example of TTL discovery] later in the docs.
    We'll discuss modifying `Expiration` in more details xref:#net-modifying-expiration[below].
For a discussion of item (Document) _vs_ Bucket expiration, see the
xref:6.5@server:learn:buckets-memory-and-storage/expiration.adoc#expiration-bucket-versus-item[Expiration Overview page].

[source,python]
                       ----
"""
# tag::expiration[]
document = {"foo": "bar", "bar": "foo"}
result = collection.upsert("document-key", document, cas=12345, expiry=timedelta(minutes=1),
                           durability=ClientDurability(ReplicateTo.ONE, PersistTo.ONE))
# end::expiration[]
"""
----

Here, we have add _Durability_ options, namely `PersistTo` and `ReplicateTo`.
    In Couchbase Server releases before 6.5, Durability was set with these two options -- see the xref:https://docs.couchbase.com/python-sdk/2.5.5/durability.html[6.0 Durability documentation] -- covering  how many replicas the operation must be propagated to and how many persisted copies of the modified record must exist.
    Couchbase Data Platform 6.5 refines these two options, with xref:synchronous-replication.adoc[Synchronous Replication] -- although they remain essentially the same in use -- as well as adding the option of xref:transactions.adoc[atomic document transactions].

The following example demonstrates using the newer durability features available in Couchbase server 6.5 onwards.

[source,python]
----
"""
# tag::upsert_syncrep[]
from couchbase.durability import Durability

document = dict(foo="bar", bar="foo")
result = collection.upsert("document-key", document,
                           cas=12345, expiry=timedelta(minutes=1),
                           durability=ServerDurability(Durability.MAJORITY))
# end::upsert_syncrep[]
"""
----

[TIP]
.Sub-Document Operations
====
All of these operations involve fetching the complete document from the Cluster.
Where the number of operations or other circumstances make bandwidth a significant issue, the SDK can work on just a specific _path_ of the document with xref:subdocument-operations.adoc[Sub-Docunent Operations].
====

== Retrieving full documents

Using the `Get()` method with the document key can be done in a similar fashion to the other operations:
    [source,python]
    ----
"""
#tag::get[]
result = collection.get("document-key")
content = result.content_as[str]
#end::get[]
"""
----
          ----


          == Removing

When removing a document, you will have the same concern for durability as with any additive modification to the Bucket:

    Remove (with options)
[source,python]
----
"""
#tag::remove_old_durability[]
result = collection.remove("document-key",
                           RemoveOptions(cas=12345, durability=ClientDurability(PersistTo.ONE, ReplicateTo.ONE)))
#end::remove_old_durability[]
"""
----

== Expiration / TTL

By default, Couchbase documents do not expire, but transient or temporary data may be needed for user sessions, caches, or other temporary documents.
Using `Touch()`, you can set expiration values on documents to handle transient data:

    [source,csharp]
    ----
"""
#tag::touch[]
result = collection.touch("document-key", timedelta(seconds=10))
#end::touch[]

"""
----

== Atomic document modifications

The value of a document can be increased or decreased atomically using `.increment()` and `.decrement()`.

    .Increment
[source,csharp]
----
// increment binary value by 1, if document doesn’t exist, seed it at 1000
"""
#tag::increment[]
collection.increment("document-key", DeltaValue(1), initial=SignedInt64(1000))
#end::increment[]
"""
---

[source,csharp]
----
.Increment (with options)
// increment binary value by 1, if document doesn’t exist, seed it at 1000
// optional arguments:
       // - Expiration (TimeSpan)
"""
#tag::increment_w_expiration[]
collection.increment("document-key", DeltaValue(1), initial=SignedInt64(1000), expiry=timedelta(days=1))
#end::increment_w_expiration[]
"""

.Decrement
 [source,csharp]
 ----
 // decrement binary value by 1, if document doesn’t exist, seed it at 1000
"""
#tag::decrement[]
collection.decrement("document-key", DeltaValue(1), initial=SignedInt64(1000))
#end::decrement[]
"""
----

.Increment (with options)
[source,csharp]
----
// decrement binary value by 1, if document doesn’t exist, seed it at 1000
// optional arguments:
       // - Expiration (TimeSpan)
"""
#tag::decrement_w_expiration[]
collection.decrement("document-key", DeltaValue(1), initial=SignedInt64(1000), expiry=timedelta(days=1))
#end::decrement_w_expiration[]
"""
----

NOTE: Increment & Decrement are considered part of the ‘binary’ API and as such may still be subject to change

                                                                                                        == Additional Resources

Working on just a specific path within a JSON document will reduce network bandwidth requirements - see the xref:subdocument-operations.adoc[Sub-Document] pages.
    For working with metadata on a document, reference our xref:sdk-xattr-example.adoc[Extended Attributes] pages.

    Another way of increasing network performance is to _pipeline_ operations with xref:batching-operations.adoc[Batching Operations].

As well as various xref:concept-docs:data-model.adoc[Formats] of JSON, Couchbase can work directly with xref:non-json.adoc[arbitary bytes, or binary format].

Our xref:n1ql-queries-with-sdk.adoc[Query Engine] enables retrieval of information using the SQL-like syntax of N1QL.

"""
